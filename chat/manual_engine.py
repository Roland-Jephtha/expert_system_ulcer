import os
import difflib
import re
import json
from collections import defaultdict

# Path configurations
KNOWLEDGE_PATH = os.path.join(os.path.dirname(__file__), 'templates', 'chat', 'knowledge.txt')
ULCER_KNOWLEDGE_PATH = os.path.join(os.path.dirname(__file__), 'templates', 'chat', 'ulcer_knowledge.txt')
STRUCTURED_FORMS_PATH = os.path.join(os.path.dirname(__file__), 'templates', 'chat', 'structured_forms.json')

# Keywords that might trigger structured question flows
MEDICAL_TRIGGERS = [
    'pain', 'headache', 'stomach', 'fever', 'cough', 'symptom', 
    'hurt', 'ache', 'sore', 'tired', 'dizzy', 'nausea', 'vomiting',
    'treatment', 'medicine', 'diagnosis', 'chest', 'heart'
]

class ConversationContext:
    """Maintains the state of a conversation with a user"""

    def __init__(self):
        self.history = []  # List of (user_msg, system_response) tuples
        self.current_form = None  # Current structured form being filled
        self.form_data = {}  # Data collected from structured forms
        self.missing_info = []  # Information we still need to collect

    def add_exchange(self, user_msg, system_response):
        """Add a message exchange to history"""
        self.history.append((user_msg, system_response))

    def start_structured_form(self, form_type):
        """Start collecting structured information"""
        self.current_form = form_type
        self.form_data = {}
        # Load the questions for this form type
        forms = load_structured_forms()
        if form_type in forms:
            self.missing_info = list(forms[form_type]['questions'].keys())
        else:
            self.missing_info = []

    def add_form_data(self, field, value):
        """Add data collected from structured form"""
        self.form_data[field] = value
        if field in self.missing_info:
            self.missing_info.remove(field)

    def is_form_complete(self):
        """Check if all required form data is collected"""
        return len(self.missing_info) == 0

    def get_next_question(self):
        """Get the next question to ask in the structured form"""
        forms = load_structured_forms()
        if not self.missing_info or self.current_form not in forms:
            return None

        next_field = self.missing_info[0]
        return forms[self.current_form]['questions'][next_field]

    def end_structured_form(self):
        """End structured form collection"""
        form_data = self.form_data
        self.current_form = None
        self.form_data = {}
        self.missing_info = []
        return form_data

    def get_recent_context(self, num_messages=3):
        """Get the recent conversation context"""
        return self.history[-num_messages:] if len(self.history) > 0 else []


def load_knowledge_base():
    """Load the knowledge base from file"""
    # Load regular knowledge base
    with open(KNOWLEDGE_PATH, 'r', encoding='utf-8') as f:
        entries = [line.strip() for line in f if line.strip()]

    # Load ulcer-specific knowledge
    try:
        with open(ULCER_KNOWLEDGE_PATH, 'r', encoding='utf-8') as f:
            ulcer_entries = [line.strip() for line in f if line.strip()]
            entries.extend(ulcer_entries)
    except FileNotFoundError:
        pass  # If ulcer knowledge file doesn't exist, just use the regular knowledge base

    return entries


def load_structured_forms():
    """Load structured form definitions"""
    try:
        with open(STRUCTURED_FORMS_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Return default forms if file doesn't exist or is invalid
        return {
            "pain_assessment": {
                "trigger_phrases": ["pain", "hurt", "ache", "sore"],
                "questions": {
                    "location": "Where exactly is the pain located?",
                    "duration": "How long have you been experiencing this pain?",
                    "intensity": "On a scale of 1-10, how would you rate the pain?",
                    "characteristics": "How would you describe the pain? (sharp, dull, throbbing, etc.)"
                },
                "follow_up_template": "Based on your description of {intensity}/10 {characteristics} pain in the {location} for {duration}, I recommend..."
            },
            "symptom_assessment": {
                "trigger_phrases": ["symptom", "fever", "cough", "dizzy", "nausea", "vomiting"],
                "questions": {
                    "main_symptom": "What is your main symptom?",
                    "duration": "How long have you been experiencing these symptoms?",
                    "severity": "How severe are your symptoms?",
                    "other_symptoms": "Are you experiencing any other symptoms?"
                },
                "follow_up_template": "Based on your {severity} {main_symptom} for {duration}, along with {other_symptoms}, I suggest..."
            }
        }


def extract_questions():
    """
    Extracts possible questions from the knowledge base.
    Assumes each entry starts with a question (ends with '?') or is formatted as 'Q: ...'
    """
    entries = load_knowledge_base()
    questions = []
    for entry in entries:
        # Try to extract question part
        match = re.match(r'(Q:)?\s*(.*?\?)', entry)
        if match:
            questions.append(match.group(2).strip())
        else:
            # Fallback: take first sentence
            first_sentence = entry.split('.')[0]
            if len(first_sentence) > 10:
                questions.append(first_sentence.strip())
    return questions


def find_best_match(query, threshold=0.5, context=None):
    """
    Find the best matching response from the knowledge base
    Enhanced with context awareness
    """
    knowledge_entries = load_knowledge_base()

    # Use context to improve matching if available
    context_boost = {}
    if context and context.history:
        # Extract keywords from recent conversation
        recent_msgs = ' '.join([msg for msg, _ in context.history[-3:]])
        # Simple keyword extraction - could be enhanced
        words = re.findall(r'\w{4,}', recent_msgs.lower())
        for word in words:
            context_boost[word] = 0.1  # Boost entries containing recent keywords

    # Use difflib to get close matches
    best_match = None
    best_score = 0.0

    for entry in knowledge_entries:
        # Base score from string similarity
        score = difflib.SequenceMatcher(None, query.lower(), entry.lower()).ratio()

        # Apply context boost
        for keyword, boost in context_boost.items():
            if keyword in entry.lower():
                score += boost

        # Check for exact phrase matches for higher precision
        phrases = extract_key_phrases(query)
        for phrase in phrases:
            if len(phrase) > 3 and phrase.lower() in entry.lower():
                score += 0.15  # Substantial boost for phrase matches

        if score > best_score:
            best_score = score
            best_match = entry

    if best_score >= threshold:
        return best_match, best_score
    else:
        return None, best_score


def extract_key_phrases(text):
    """Extract potential key phrases from text"""
    # Simple approach: split by common delimiters
    phrases = []
    for delimiter in ['.', ',', ';', '?', '!']:
        parts = text.split(delimiter)
        phrases.extend([p.strip() for p in parts if len(p.strip()) > 0])

    # Add noun phrases (simplified approach)
    words = text.split()
    for i in range(len(words) - 1):
        phrases.append(f"{words[i]} {words[i+1]}")

    return phrases


def check_needs_structured_form(user_message, context):
    """
    Check if the user's message indicates we should switch to structured form
    Returns the form_type if needed, None otherwise
    """
    # Skip if already in a structured form
    if context and context.current_form:
        return None

    # Load form definitions
    forms = load_structured_forms()

    # Check for trigger phrases in each form
    message_lower = user_message.lower()

    for form_type, form_def in forms.items():
        trigger_phrases = form_def.get('trigger_phrases', [])
        for phrase in trigger_phrases:
            if phrase.lower() in message_lower:
                return form_type

    # No triggers found
    return None


def process_structured_form_input(user_message, context):
    """Process user input for a structured form question"""
    if not context or not context.current_form:
        return None

    # Get the current field being asked
    current_field = context.missing_info[0] if context.missing_info else None
    if not current_field:
        return None

    # Store the user's answer for this field
    context.add_form_data(current_field, user_message)

    # Check if we've completed the form
    if context.is_form_complete():
        form_type = context.current_form
        form_data = context.form_data.copy()
        forms = load_structured_forms()

        # Generate specific responses based on ulcer diagnosis
        if form_type == "ulcer_diagnosis":
            response = generate_ulcer_diagnosis_response(form_data)
        elif form_type == "ulcer_treatment":
            response = generate_ulcer_treatment_response(form_data)
        elif form_type == "ulcer_diet":
            response = generate_ulcer_diet_response(form_data)
        elif form_type == "ulcer_lifestyle":
            response = generate_ulcer_lifestyle_response(form_data)
        else:
            # Generate response using the template
            if form_type in forms and 'follow_up_template' in forms[form_type]:
                template = forms[form_type]['follow_up_template']
                try:
                    response = template.format(**form_data)
                except KeyError:
                    response = f"Thank you for providing that information about your {form_type}."
            else:
                response = f"Thank you for providing that information about your {form_type}."

        # End the form
        context.end_structured_form()
        return response

    # Get the next question
    next_question = context.get_next_question()
    return next_question

def generate_ulcer_diagnosis_response(form_data):
    """Generate a specific ulcer diagnosis response based on user input"""
    pain_location = form_data.get("pain_location", "")
    pain_timing = form_data.get("pain_timing", "")
    pain_severity = form_data.get("pain_severity", "")
    pain_description = form_data.get("pain_description", "")
    other_symptoms = form_data.get("other_symptoms", "")
    nsaids_use = form_data.get("nsaids_use", "")
    alcohol = form_data.get("alcohol", "")
    smoking = form_data.get("smoking", "")
    stress = form_data.get("stress", "")

    # Determine ulcer type based on symptoms
    ulcer_type = "gastric ulcer"
    if "lower chest" in pain_location.lower() or "behind breastbone" in pain_location.lower():
        if "improves" in pain_timing.lower() or "better after" in pain_timing.lower():
            ulcer_type = "duodenal ulcer"
        elif "worsens" in pain_timing.lower() or "worse when" in pain_timing.lower():
            ulcer_type = "esophageal ulcer"

    # Generate treatment recommendations
    treatment_recommendations = ""
    if ulcer_type == "gastric ulcer":
        treatment_recommendations = "For gastric ulcers, take Omeprazole 20mg twice daily before meals for 4-8 weeks. If H. pylori is suspected, you'll need antibiotics: Amoxicillin 500mg twice daily and Clarithromycin 500mg twice daily for 14 days."
    elif ulcer_type == "duodenal ulcer":
        treatment_recommendations = "For duodenal ulcers, take Omeprazole 20mg twice daily before meals for 4-8 weeks. If H. pylori is suspected, you'll need antibiotics: Amoxicillin 500mg twice daily and Clarithromycin 500mg twice daily for 14 days."
    elif ulcer_type == "esophageal ulcer":
        treatment_recommendations = "For esophageal ulcers, take Omeprazole 20mg twice daily before meals for 4-8 weeks. Additionally, take an H2 blocker like Ranitidine 150mg twice daily. Avoid lying down for at least 3 hours after eating."

    # Generate dietary recommendations
    diet_recommendations = "Eat smaller, more frequent meals throughout the day. Focus on high-fiber foods like oats, brown rice, and vegetables. Include probiotic-rich foods like yogurt and kefir. Avoid spicy foods, fatty foods, caffeine, alcohol, and chocolate."

    # Format the response
    response = f"Based on your symptoms, particularly the {pain_severity}/10 {pain_description} pain in the {pain_location} that occurs {pain_timing}, along with {other_symptoms}, and considering your risk factors like {nsaids_use}, {alcohol} consumption, {smoking}, and {stress} levels, you may have a {ulcer_type}. {treatment_recommendations} {diet_recommendations}"

    return response

def generate_ulcer_treatment_response(form_data):
    """Generate a specific ulcer treatment response based on user input"""
    ulcer_type = form_data.get("ulcer_type", "gastric ulcer")
    current_treatment = form_data.get("current_treatment", "none")
    medication_allergies = form_data.get("medication_allergies", "none")
    treatment_goals = form_data.get("treatment_goals", "pain relief and healing")

    # Generate treatment recommendations
    treatment_recommendations = ""
    if ulcer_type == "gastric ulcer":
        treatment_recommendations = "For gastric ulcers, take Omeprazole 20mg twice daily before meals for 4-8 weeks. If H. pylori is suspected, you'll need antibiotics: Amoxicillin 500mg twice daily and Clarithromycin 500mg twice daily for 14 days."
    elif ulcer_type == "duodenal ulcer":
        treatment_recommendations = "For duodenal ulcers, take Omeprazole 20mg twice daily before meals for 4-8 weeks. If H. pylori is suspected, you'll need antibiotics: Amoxicillin 500mg twice daily and Clarithromycin 500mg twice daily for 14 days."
    elif ulcer_type == "esophageal ulcer":
        treatment_recommendations = "For esophageal ulcers, take Omeprazole 20mg twice daily before meals for 4-8 weeks. Additionally, take an H2 blocker like Ranitidine 150mg twice daily. Avoid lying down for at least 3 hours after eating."

    # Generate dietary recommendations
    diet_recommendations = "Eat smaller, more frequent meals throughout the day. Focus on high-fiber foods like oats, brown rice, and vegetables. Include probiotic-rich foods like yogurt and kefir. Avoid spicy foods, fatty foods, caffeine, alcohol, and chocolate."

    # Generate lifestyle recommendations
    lifestyle_recommendations = "Avoid smoking, limit alcohol consumption, manage stress through relaxation techniques, and don't lie down immediately after eating. Elevate the head of your bed when sleeping."

    # Format the response
    response = f"For {ulcer_type} ulcers, {treatment_recommendations} {diet_recommendations} {lifestyle_recommendations}"

    return response

def generate_ulcer_diet_response(form_data):
    """Generate a specific ulcer diet response based on user input"""
    food_preferences = form_data.get("food_preferences", "")
    allergies = form_data.get("allergies", "")
    cooking_style = form_data.get("cooking_style", "")

    # Generate foods to eat
    foods_to_eat = "High-fiber foods: oats, barley, brown rice, whole grains. Probiotic-rich foods: yogurt, kefir, sauerkraut. Vitamin-rich fruits and vegetables: sweet potatoes, spinach, carrots. Lean proteins: skinless poultry, fish, tofu. Healthy fats: olive oil, avocado."

    # Generate foods to avoid
    foods_to_avoid = "Spicy foods: hot peppers, chili, curry. Fatty or greasy foods: fried foods, fatty meats. Highly acidic foods: tomatoes, citrus, vinegar. Caffeine: coffee, strong tea. Carbonated beverages. Alcohol. Chocolate. Processed snacks high in salt, sugar, or preservatives."

    # Generate meal plan
    meal_plan = "Breakfast: Oatmeal with bananas and honey. Lunch: Grilled chicken salad with olive oil dressing. Dinner: Baked salmon with steamed vegetables and brown rice. Snacks: Yogurt with berries, almonds, or rice cakes."

    # Format the response
    response = f"Based on your preferences, here are dietary recommendations for ulcers: {foods_to_eat} {foods_to_avoid} {meal_plan}"

    return response

def generate_ulcer_lifestyle_response(form_data):
    """Generate a specific ulcer lifestyle response based on user input"""
    stress_level = form_data.get("stress_level", "")
    sleep_quality = form_data.get("sleep_quality", "")
    exercise_frequency = form_data.get("exercise_frequency", "")
    alcohol_consumption = form_data.get("alcohol_consumption", "")
    smoking_status = form_data.get("smoking_status", "")

    # Generate stress management recommendations
    stress_management = "Manage stress through relaxation techniques like deep breathing, meditation, or yoga. Consider practicing mindfulness or tai chi."

    # Generate sleep habits recommendations
    sleep_habits = "Improve sleep quality by maintaining a consistent sleep schedule. Create a relaxing bedtime routine. Keep your bedroom cool, dark, and quiet. Avoid screens before bedtime."

    # Generate exercise recommendations
    exercise_recommendations = "Engage in moderate exercise like walking, swimming, or cycling for at least 30 minutes most days of the week. Avoid intense exercise that may stress your digestive system."

    # Generate alcohol advice
    alcohol_advice = "Limit alcohol consumption or avoid it completely. If you do drink, do so in moderation and with food."

    # Generate smoking cessation advice
    smoking_cessation = "Quit smoking to help your ulcers heal. Consider nicotine replacement therapy or seek professional help to quit."

    # Format the response
    response = f"Based on your lifestyle factors, here are recommendations for managing ulcers: {stress_management} {sleep_habits} {exercise_recommendations} {alcohol_advice} {smoking_cessation}"

    return response


# Global dictionary to store conversation contexts
contexts = {}

def process_message(user_message, session_id=None, contexts_dict=None):
    """
    Process a user message, using session context if available
    Returns (response, is_structured_form_question)
    """
    # Initialize or retrieve conversation context
    if contexts_dict is None:
        contexts_dict = contexts

    if session_id not in contexts_dict:
        contexts_dict[session_id] = ConversationContext()

    context = contexts_dict[session_id]

    # If we're in a structured form, process input for it
    if context.current_form:
        form_response = process_structured_form_input(user_message, context)
        if form_response:
            context.add_exchange(user_message, form_response)
            return form_response, True

    # Check if we need to switch to a structured form
    form_type = check_needs_structured_form(user_message, context)
    if form_type:
        context.start_structured_form(form_type)
        next_question = context.get_next_question()
        if next_question:
            context.add_exchange(user_message, next_question)
            return next_question, True

    # Otherwise, find a matching response from knowledge base
    best_match, best_score = find_best_match(user_message, threshold=0.5, context=context)

    if best_match:
        response = best_match
    else:
        response = "Sorry, I couldn't find a relevant answer. Could you provide more details or ask another question?"

    context.add_exchange(user_message, response)
    return response, False

