// Make setInput globally accessible
window.setInput = function(text) {
    const input = document.getElementById('message-input');
    const form = document.getElementById('input-form');

    if (!input || !form) return;

    input.value = text;
    input.focus();
    // Trigger form submission
    form.dispatchEvent(new Event('submit'));
};

// Make setInputOnly globally accessible
window.setInputOnly = function(text) {
    const input = document.getElementById('message-input');

    if (!input) return;

    input.value = text;
    input.focus();
};

// Predefined answers for common questions
const questionAnswers = {
    "What should I eat if I have an ulcer?": "If you have an ulcer, you should eat a diet that's high in fiber and rich in vitamins. Focus on foods like:\n\n• High-fiber foods: Oats, barley, brown rice, whole grains, beans, lentils, apples, pears, bananas, carrots, broccoli, and leafy greens.\n• Probiotic-rich foods: Yogurt with live cultures, kefir, sauerkraut, miso, kimchi, and tempeh to help balance gut bacteria.\n• Vitamin A-rich foods: Sweet potatoes, spinach, kale, carrots, pumpkin.\n• Vitamin C-rich foods: Oranges, papaya, strawberries, kiwi, tomatoes, bell peppers.\n• Zinc-rich foods: Pumpkin seeds, cashews, lean beef, turkey, seafood.\n• Gentle proteins: Skinless poultry, fish, tofu, eggs, low-fat dairy.\n• Healthy fats: Olive oil, flaxseed oil, avocado, nuts (in moderation).\n\nEat smaller, more frequent meals throughout the day and avoid lying down immediately after eating.",

    "What foods should I avoid with an ulcer?": "If you have an ulcer, you should avoid foods that can aggravate your symptoms:\n\n• Spicy foods: Hot peppers, chili, curry, wasabi.\n• Fatty or greasy foods: Fried foods, fatty meats, creamy sauces.\n• Highly acidic foods: Tomatoes, citrus fruits, vinegar, soda.\n• Caffeine: Coffee, strong tea, chocolate.\n• Carbonated beverages: Soda, sparkling water.\n• Alcohol: Beer, wine, spirits.\n• Excess milk: Can increase acid production.\n• Processed snacks: High in salt, sugar, or preservatives.\n\nThese foods can increase stomach acid production and irritate the ulcer, potentially worsening your symptoms.",

    "What are the symptoms of a stomach ulcer?": "Common symptoms of a stomach ulcer (gastric ulcer) include:\n\n• Burning or gnawing pain in the upper abdomen, typically between the breastbone and navel\n• Pain that worsens when the stomach is empty (often occurs 2-3 hours after eating or during the night)\n• Pain that may temporarily be relieved by eating or taking antacids\n• Bloating or feeling full after eating small amounts\n• Nausea or vomiting\n• Loss of appetite and weight loss\n• Dark or tarry stools (a sign of bleeding)\n• Fatigue (due to anemia from blood loss)\n\nIn severe cases, ulcers can cause:\n• Severe abdominal pain\n• Vomiting blood (which may appear red or black)\n• Dark blood in stools or black, tarry stools\n• Trouble breathing\n• Feeling faint or dizzy\n\nIf you experience severe symptoms, seek immediate medical attention.",

    "How are ulcers treated?": "Ulcers are typically treated with a combination of medications and lifestyle changes:\n\n**Medications:**\n• Proton Pump Inhibitors (PPIs): Reduce stomach acid production. Common PPIs include omeprazole (Prilosec), lansoprazole (Prevacid), and esomeprazole (Nexium).\n• H2 Blockers: Reduce stomach acid production. Examples include ranitidine (Zantac), famotidine (Pepcid), and cimetidine (Tagamet).\n• Antibiotics: If your ulcer is caused by H. pylori bacteria, you'll need antibiotics. Common combinations include amoxicillin and clarithromycin.\n• Bismuth Subsalicylate: Helps protect the ulcer from stomach acid.\n\n**Lifestyle Changes:**\n• Avoid smoking and alcohol\n• Avoid NSAIDs (like aspirin, ibuprofen, and naproxen) if possible\n• Manage stress through relaxation techniques\n• Eat a balanced diet with smaller, more frequent meals\n• Avoid foods that aggravate your symptoms\n\n**Follow-up:**\n• Take all medications as prescribed\n• Follow up with your healthcare provider\n• Complete all antibiotic courses if prescribed\n• Get tested for H. pylori eradication if treated for it\n\nMost ulcers heal within 4-8 weeks with proper treatment.",

    "What causes ulcers?": "Ulcers can be caused by several factors:\n\n1. **H. pylori infection:** This is the most common cause of ulcers. H. pylori is a type of bacteria that can damage the protective mucous coating of the stomach and small intestine, allowing acid to get through to the sensitive lining beneath.\n\n2. **Regular use of NSAIDs:** Nonsteroidal anti-inflammatory drugs (NSAIDs) can irritate the stomach lining and reduce the production of prostaglandins, which help protect the stomach from acid damage. Common NSAIDs include aspirin, ibuprofen (Advil, Motrin), and naproxen (Aleve).\n\n3. **Excessive alcohol consumption:** Alcohol can irritate and erode the mucous lining of your stomach, increasing stomach acid production.\n\n4. **Smoking:** Smoking increases stomach acid production, reduces the production of prostaglandins, and reduces blood flow to the stomach, which can slow healing.\n\n5. **Stress:** While stress doesn't directly cause ulcers, it can make symptoms worse and slow healing.\n\n6. **Zollinger-Ellison syndrome:** This rare condition causes tumors in the pancreas or duodenum that produce excessive amounts of acid, which can lead to ulcers.\n\nIn many cases, ulcers are caused by a combination of these factors.",

    "How can I prevent ulcers?": "You can reduce your risk of developing ulcers by:\n\n1. **Practice good hygiene:** Wash your hands thoroughly with soap and water to reduce your risk of H. pylori infection.\n\n2. **Use NSAIDs wisely:**\n   • Use the lowest effective dose for the shortest time possible\n   • Take NSAIDs with food or a protective medication if needed long-term\n   • Consider alternatives like acetaminophen for pain relief\n\n3. **Limit alcohol consumption:** Excessive alcohol can irritate your stomach lining and increase stomach acid production.\n\n4. **Don't smoke:** Smoking increases stomach acid production, reduces prostaglandins, and reduces blood flow to the stomach.\n\n5. **Manage stress:** Practice stress-reduction techniques like meditation, deep breathing, yoga, or regular exercise.\n\n6. **Eat a healthy diet:** Focus on fruits, vegetables, whole grains, and lean proteins. Avoid spicy, fatty, or acidic foods that can irritate your stomach.\n\n7. **Maintain a healthy weight:** Excess weight can increase pressure on your abdomen, which can contribute to acid reflux and ulcers.\n\n8. **Get treatment for H. pylori:** If you have H. pylori infection, get it treated to prevent ulcers.\n\nIf you have a history of ulcers or are at high risk, talk to your healthcare provider about preventive measures.",

    "What is the difference between gastric and duodenal ulcers?": "Gastric ulcers and duodenal ulcers are both types of peptic ulcers, but they differ in location and characteristics:\n\n**Gastric Ulcers (Stomach Ulcers):**\n• Location: Occur in the lining of the stomach\n• Pain timing: Often worsens after eating\n• Common symptoms: Nausea, bloating, feeling full quickly, weight loss\n• Causes: H. pylori infection, NSAID use, stress, Zollinger-Ellison syndrome\n• Treatment: Similar to duodenal ulcers, but may require longer treatment with PPIs\n\n**Duodenal Ulcers:**\n• Location: Occur in the first part of the small intestine (duodenum)\n• Pain timing: Often improves after eating and may wake you at night\n• Common symptoms: Heartburn, acid reflux, more predictable pain patterns\n• Causes: H. pylori infection, NSAID use, smoking\n• Treatment: Typically heal faster than gastric ulcers\n\n**Similarities:**\n• Both types of ulcers are caused by damage to the protective mucous layer of the digestive tract\n• Both can be treated with medications that reduce stomach acid and antibiotics if H. pylori is present\n• Both can cause complications like bleeding, perforation, or obstruction if left untreated\n\n**Diagnosis:** Both types are typically diagnosed through endoscopy, upper GI series, or tests for H. pylori infection.",

    "How long does it take for an ulcer to heal?": "The healing time for ulcers depends on several factors including the type of ulcer, its size, the cause, and the treatment approach:\n\n**With proper treatment:**\n• Most gastric ulcers heal within 6-8 weeks\n• Most duodenal ulcers heal within 4-6 weeks\n• Esophageal ulcers may take 8-12 weeks to heal\n\n**Factors affecting healing time:**\n• Size and depth of the ulcer\n• Cause (H. pylori vs. NSAID-induced)\n• Adherence to treatment plan\n• Overall health and age\n• Smoking and alcohol use\n• Stress levels\n\n**Treatment duration:**\n• Acid-reducing medications (PPIs or H2 blockers): 4-8 weeks\n• Antibiotics for H. pylori: 10-14 days\n• Follow-up testing for H. pylori: 4 weeks after completing antibiotics\n\n**Signs of healing:**\n• Reduction in pain and other symptoms\n• Improvement in appetite and weight\n• Healing of the ulcer as seen on follow-up endoscopy (if performed)\n\nIf ulcers don't heal with standard treatment, your healthcare provider may recommend additional testing or different treatment approaches. In rare cases, surgery may be needed to treat complications or ulcers that don't respond to other treatments."
};

// Function to handle question clicks
async function handleQuestionClick(question) {
    // Get references to DOM elements
    const startChatButton = document.getElementById('start-chat-button');
    const form = document.getElementById('input-form');
    const input = document.getElementById('message-input');
    const messages = document.getElementById('messages');
    const typingIndicator = document.getElementById('typing-indicator');
    const suggestionsContainer = document.getElementById('suggestions-container');

    // Play send sound
    try {
        const sendSound = new Audio('/static/chat/audio/send.mp3');
        sendSound.play().catch(e => console.log('Send sound play error:', e));
    } catch (e) {
        console.log('Send sound error:', e);
    }

    // Check if the start chat button is visible
    if (startChatButton && startChatButton.style.display !== 'none') {
        // Hide the start button
        startChatButton.style.display = 'none';

        // Add welcome message
        appendMessage('bot', "Hello! I'm your ulcer specialist assistant. I can help you with questions about ulcers, treatments, diet, and lifestyle changes.");

        // Wait a moment before adding the question
        await new Promise(resolve => setTimeout(resolve, 500));
    }

    // Add the question as a user message
    appendMessage('user', question);

    // Show typing indicator and play typing sound
    showTypingIndicator();

    try {
        const typingSound = new Audio('/static/chat/audio/typing.mp3');
        typingSound.play().catch(e => console.log('Typing sound play error:', e));
    } catch (e) {
        console.log('Typing sound error:', e);
    }

    // Simulate processing time
    setTimeout(() => {
        // Hide typing indicator
        hideTypingIndicator();

        // Get the predefined answer
        let answer = questionAnswers[question];

        if (answer) {
            // Use the predefined answer
            appendMessage('bot', answer);

            // Add follow-up suggestions
            setTimeout(() => {
                showSuggestions([
                    "What should I eat if I have an ulcer?",
                    "What foods should I avoid with an ulcer?",
                    "What are the symptoms of a stomach ulcer?"
                ]);
            }, 1000);
        } else {
            // If no predefined answer, use the existing system to get a response
            fetch('', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': getCookie('csrftoken'),
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: `message=${encodeURIComponent(question)}`
            })
            .then(response => response.json())
            .then(data => {
                appendMessage('bot', data.response);

                // Add follow-up suggestions
                setTimeout(() => {
                    showSuggestions([
                        "What should I eat if I have an ulcer?",
                        "What foods should I avoid with an ulcer?",
                        "What are the symptoms of a stomach ulcer?"
                    ]);
                }, 1000);
            })
            .catch(error => {
                console.error('Error:', error);
                appendMessage('bot', "I'm sorry, I encountered an error. Please try again.");
            });
        }
    }, 1000);
}

// Function to append a message to the chat
function appendMessage(sender, message) {
    const messages = document.getElementById('messages');
    const messageElement = document.createElement('div');
    messageElement.className = `message ${sender}-message`;

    // Replace newlines with <br> tags
    const formattedMessage = message.replace(/\n/g, '<br>');
    messageElement.innerHTML = formattedMessage;

    messages.appendChild(messageElement);
    messages.scrollTop = messages.scrollHeight;
}

// Function to show typing indicator
function showTypingIndicator() {
    const messages = document.getElementById('messages');
    const typingIndicator = document.createElement('div');
    typingIndicator.className = 'message bot-message typing-indicator';
    typingIndicator.innerHTML = '<span class="typing-dots"><span>.</span><span>.</span><span>.</span></span>';

    messages.appendChild(typingIndicator);
    messages.scrollTop = messages.scrollHeight;
}

// Function to hide typing indicator
function hideTypingIndicator() {
    const typingIndicator = document.querySelector('.typing-indicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

// Function to show suggestions
function showSuggestions(suggestions) {
    const suggestionsContainer = document.getElementById('suggestions-container');
    suggestionsContainer.innerHTML = '';

    suggestions.forEach(suggestion => {
        const chip = document.createElement('div');
        chip.className = 'suggestion-chip';
        chip.textContent = suggestion;
        chip.onclick = () => handleQuestionClick(suggestion);
        suggestionsContainer.appendChild(chip);
    });
}

// Function to get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Initialize chat when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Get references to DOM elements
    const startChatButton = document.getElementById('start-chat-button');
    const form = document.getElementById('input-form');
    const input = document.getElementById('message-input');
    const messages = document.getElementById('messages');
    const suggestionsContainer = document.getElementById('suggestions-container');

    // Initialize the Start Chat button
    if (startChatButton) {
        startChatButton.addEventListener('click', () => {
            startChatButton.style.display = 'none';
            appendMessage('bot', "Hello! I'm your ulcer specialist assistant. I can help you with questions about ulcers, treatments, diet, and lifestyle changes.");

            // Show initial suggestions
            setTimeout(() => {
                showSuggestions([
                    "What should I eat if I have an ulcer?",
                    "What foods should I avoid with an ulcer?",
                    "What are the symptoms of a stomach ulcer?"
                ]);
            }, 1000);
        });
    }

    // Handle form submission
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();

            // Play send sound
            try {
                const sendSound = new Audio('/static/chat/audio/send.mp3');
                sendSound.play().catch(e => console.log('Send sound play error:', e));
            } catch (e) {
                console.log('Send sound error:', e);
            }

            const message = input.value.trim();
            if (message) {
                appendMessage('user', message);
                input.value = '';

                // Show typing indicator and play typing sound
                showTypingIndicator();

                try {
                    const typingSound = new Audio('/static/chat/audio/typing.mp3');
                    typingSound.play().catch(e => console.log('Typing sound play error:', e));
                } catch (e) {
                    console.log('Typing sound error:', e);
                }

                // Send message to server
                fetch('', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'X-CSRFToken': getCookie('csrftoken'),
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    body: `message=${encodeURIComponent(message)}`
                })
                .then(response => response.json())
                .then(data => {
                    hideTypingIndicator();
                    appendMessage('bot', data.response);

                    // Add follow-up suggestions
                    setTimeout(() => {
                        showSuggestions([
                            "What should I eat if I have an ulcer?",
                            "What foods should I avoid with an ulcer?",
                            "What are the symptoms of a stomach ulcer?"
                        ]);
                    }, 1000);
                })
                .catch(error => {
                    hideTypingIndicator();
                    console.error('Error:', error);
                    appendMessage('bot', "I'm sorry, I encountered an error. Please try again.");
                });
            }
        });
    }
});
