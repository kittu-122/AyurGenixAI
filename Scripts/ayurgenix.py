from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer
import torch
import pandas as pd

# Free GPU Memory Before Running
torch.cuda.empty_cache()

# Path to the model
modelPath = "C:\\codes\\llama1B\\"

# Load the dataset
dataset_path = "C:\\codes\\llama1B\\AyurGenixAI_Dataset.csv"
data = pd.read_csv(dataset_path)

# Preprocess the dataset
def generate_context_from_dataset(data):
    """Generate a context string based on the dataset."""
    context = "\n".join(
        f"Symptom: {row['Symptoms']}, Disease: {row['Disease']}, Hindi Name: {row['Hindi Name']}, Marathi Name: {row['Marathi Name']}, Remedies: {row['Herbal/Alternative Remedies']}"
        for _, row in data.iterrows()
    )
    return context

dataset_context = generate_context_from_dataset(data)

# Load Model in 8-bit for Reduced Memory Usage
model = AutoModelForCausalLM.from_pretrained(
    modelPath,
    torch_dtype=torch.float16,  # Use 16-bit floating point for efficiency
    device_map="auto",          # Automatically assigns layers to GPU
    load_in_8bit=True           # Load model in 8-bit mode to save VRAM
)

# Load tokenizer
tokenizer = AutoTokenizer.from_pretrained(modelPath)

# Initialize the text-generation pipeline
pipe = pipeline("text-generation", model=model, tokenizer=tokenizer)

# Function to retrieve relevant data based on symptoms
def retrieve_relevant_data(user_input, data):
    """Filter dataset to find relevant diseases based on symptoms."""
    relevant_rows = data[data["Symptoms"].str.contains(user_input, case=False, na=False)]
   
    if relevant_rows.empty:
        return "No direct match found in dataset. Proceeding with Ayurvedic general knowledge."
   
    return "\n".join(
        f"Symptom: {row['Symptoms']}, Disease: {row['Disease']}, Hindi Name: {row['Hindi Name']}, Marathi Name: {row['Marathi Name']}, Remedies: {row['Herbal/Alternative Remedies']}"
        for _, row in relevant_rows.iterrows()
    )

# Take user input dynamically
user_message = input("Please describe your symptoms and concerns: ")

# Get relevant dataset rows based on symptoms
filtered_context = retrieve_relevant_data(user_message, data)

# Create prompt
input_prompt = f"""
### Context:
{filtered_context}

### Instruction:

You are an experienced Ayurvedic practitioner. Your role is to assist users by analyzing their health conditions based on provided symptoms and creating a concise, user-friendly health report. Ensure your responses align with Ayurvedic principles and terminology while maintaining accuracy and clarity.

The report must include the following sections, each expressed in a  line:

1. Disease: List the likely conditions based on the provided symptoms.
2. Hindi Name: Provide the disease name in Hindi (use Romanized Hindi if necessary).
3. Marathi Name: Provide the disease name in Marathi (use Romanized Marathi if necessary).
4. Diagnosis & Tests: Suggest diagnostic tests or methods for confirmation.
5. Duration of Treatment: Estimate the recovery period or treatment duration.
6. Risk Factors: Mention any contributing or aggravating factors.
7. Environmental Factors: Discuss the impact of seasons or surroundings on the condition.
8. Herbal/Alternative Remedies: Suggest non-pharmaceutical interventions for relief.
9. Ayurvedic Herbs: Recommend specific herbs useful for the condition.
10. Formulation: Suggest appropriate Ayurvedic formulations or recipes.
11. Diet and Lifestyle Recommendations: Tailor suggestions to the patient’s doshas and constitution.
12. Yoga & Physical Therapy: Recommend yoga asanas or therapies for support.
13. Medical Intervention: Specify conditions requiring modern medical attention.
14. Prevention: Provide preventive measures to avoid recurrence.
15. Prognosis: Outline expected outcomes and future considerations.
16. Complications: Warn about risks if untreated or improperly managed.
17. Patient Recommendations: Summarize actionable steps for the user to follow.

---

### Important Notes and Disclaimers:
1. Personalized Insights: Tailor responses to the user's unique information and cultural context.
2. Accuracy: Base your report on the details provided, and clearly state if certain conclusions cannot be made due to insufficient data.

3. Ayurvedic Principles: Ensure all recommendations are rooted in Ayurvedic principles and are holistic in nature.
4. Language: Use simple language to make the report easily understandable for users from diverse backgrounds.   

---

Ensure accuracy and clarity while maintaining Ayurvedic principles.
"""

# Generate response (with reduced token limit)
response = pipe(input_prompt, max_new_tokens=1000, temperature=0.7, top_k=50)


# Extract and print the generated text
outputResponse = response[0]["generated_text"]
print(outputResponse)

# Save the response to a file
with open('updated-op.txt', 'w', encoding="utf-8") as text_file:
    text_file.write(outputResponse)