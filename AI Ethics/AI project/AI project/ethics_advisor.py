import tkinter as tk
from tkinter import ttk, scrolledtext
import google.generativeai as genai
import threading
import os
import queue
from queue import Empty
from PIL import Image, ImageTk
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class MusicTheoryTrainer:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Ethics Advisor")
        self.root.geometry("900x700")
        self.root.minsize(600, 500)
        
        # Custom colors
        self.bg_color = "#1E1E2E"  # Dark background
        self.accent_color = "#F28C28"  # Orange accent
        self.text_color = "#FFFFFF"  # White text
        self.secondary_color = "#2D2D44"  # Darker purple for contrast
        self.highlight_color = "#89B4FA"  # Light blue highlight
        
        # Owner information
        self.owner = "Harshvardhan Singh"
        
        # Team member details
        self.team_members = [
            {"name": "Harshvardhan", "id": "12303425"},
            {"name": "Sarthak", "id": "12303986"},
            {"name": "Prakhar", "id": "12313487"}
        ]
        
        # Configure root background
        self.root.configure(bg=self.bg_color)
        
        # Configure styles with modern UI
        self.style = ttk.Style()
        self.style.theme_use('default')
        
        # Configure styles
        self.style.configure("TFrame", background=self.bg_color)
        self.style.configure("Secondary.TFrame", background=self.secondary_color)
        
        self.style.configure("TButton", 
                             background=self.accent_color, 
                             foreground=self.text_color, 
                             font=('Helvetica', 11, 'bold'),
                             borderwidth=0)
        self.style.map("TButton",
                      background=[('active', self.highlight_color), ('pressed', self.accent_color)],
                      foreground=[('active', self.text_color), ('pressed', self.text_color)])
                      
        self.style.configure("TLabel", 
                             background=self.bg_color, 
                             foreground=self.text_color, 
                             font=('Helvetica', 11))
        
        self.style.configure("Header.TLabel", 
                             background=self.bg_color, 
                             foreground=self.accent_color, 
                             font=('Helvetica', 16, 'bold'))
                             
        self.style.configure("TNotebook", 
                             background=self.bg_color, 
                             foreground=self.text_color,
                             tabmargins=[2, 5, 2, 0])
        
        self.style.configure("TNotebook.Tab", 
                             background=self.secondary_color, 
                             foreground=self.text_color,
                             padding=[15, 5],
                             font=('Helvetica', 10, 'bold'))
                             
        self.style.map("TNotebook.Tab",
                      background=[("selected", self.accent_color)],
                      foreground=[("selected", self.text_color)])

        # Create notebook (tabs) with custom style
        self.notebook = ttk.Notebook(self.root)
        
        # Chat Tab
        self.chat_frame = ttk.Frame(self.notebook, style="TFrame")
        self.notebook.add(self.chat_frame, text="Chat")

        # Instructions Tab
        self.instructions_frame = ttk.Frame(self.notebook, style="TFrame")
        self.notebook.add(self.instructions_frame, text="Instructions")

        self.notebook.pack(expand=True, fill="both", padx=10, pady=10)

        # Set up chat tab
        self.setup_chat_tab()

        # Set up instructions tab
        self.setup_instructions_tab()

        # API Details for Gemini
        self.api_key = "AIzaSyAcclQtZHF8mD9ajtu5Xva80_JQDO9-7KY"
        
        if not self.api_key:
            self.show_error("API key missing. Set the GOOGLE_API_KEY in your environment.")
            return  # Prevent further execution

        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-pro-latest')
        except Exception as e:
            self.show_error(f"Failed to configure AI model: {str(e)}")
            return

        self.response_queue = queue.Queue()
        self.root.after(100, self.process_queue)

    def process_queue(self):
        """Process messages from the queue in the main thread"""
        try:
            message = self.response_queue.get_nowait()
            self.update_chat_display(message)
            self.response_queue.task_done()
        except Empty:
            pass
        self.root.after(100, self.process_queue)

    def setup_chat_tab(self):
        # Header with icon frame
        header_frame = ttk.Frame(self.chat_frame, style="TFrame")
        header_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Title with music note emoji
        title_label = ttk.Label(header_frame, 
                                text="🧠 AI Ethics Advisor 🧠", 
                                style="Header.TLabel")
        title_label.pack(pady=10)
        
        # Description subtitle
        subtitle = ttk.Label(header_frame, 
                             text="Your personal assistant for learning ethics in Hinglish",
                             style="TLabel")
        subtitle.pack(pady=(0, 10))
        
        # Chat display with custom colors
        chat_frame = ttk.Frame(self.chat_frame, style="Secondary.TFrame")
        chat_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame, 
            wrap=tk.WORD, 
            width=80, 
            height=20, 
            font=("Helvetica", 10),
            bg=self.secondary_color,
            fg=self.text_color,
            insertbackground=self.text_color,
            selectbackground=self.highlight_color,
            relief=tk.FLAT
        )
        self.chat_display.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.chat_display.config(state=tk.DISABLED)
        
        # Add welcome message
        self.chat_display.config(state=tk.NORMAL)
        welcome_message = "Welcome to AI Ethics Advisor! Ask me any question about ethics in Hindi or English. 🧠\n\n"
        self.chat_display.insert(tk.END, welcome_message)
        self.chat_display.tag_configure("welcome", foreground=self.highlight_color, font=("Helvetica", 10, "italic"))
        self.chat_display.tag_add("welcome", "1.0", "end")
        self.chat_display.config(state=tk.DISABLED)

        # Input frame with rounded appearance
        input_frame = ttk.Frame(self.chat_frame, style="Secondary.TFrame")
        input_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Create a custom entry with rounded corners using a Canvas
        entry_frame = ttk.Frame(input_frame, style="Secondary.TFrame")
        entry_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)
        
        self.question_input = tk.Entry(
            entry_frame, 
            font=("Helvetica", 11),
            bg=self.secondary_color,
            fg=self.text_color,
            insertbackground=self.text_color,
            relief=tk.FLAT,
            highlightthickness=1,
            highlightbackground=self.accent_color,
            highlightcolor=self.highlight_color
        )
        self.question_input.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8, padx=10)
        self.question_input.bind("<Return>", lambda event: self.send_question())
        
        # Send button with improved styling
        send_button = tk.Button(
            input_frame, 
            text="Send ➤",
            font=("Helvetica", 11, "bold"),
            bg=self.accent_color,
            fg=self.text_color,
            activebackground=self.highlight_color,
            activeforeground=self.text_color,
            relief=tk.FLAT,
            padx=15,
            pady=8,
            command=self.send_question
        )
        send_button.pack(side=tk.RIGHT, padx=5)

        # Status bar with modern look
        status_frame = ttk.Frame(self.root, style="Secondary.TFrame")
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_bar = ttk.Label(
            status_frame, 
            textvariable=self.status_var, 
            style="TLabel",
            padding=(10, 5)
        )
        self.status_bar.pack(side=tk.LEFT)
        
        # Add developer info to status bar
        dev_info = ttk.Label(
            status_frame,
            text=f"Developed by: {self.owner}",
            style="TLabel",
            padding=(10, 5)
        )
        dev_info.pack(side=tk.RIGHT)

    def setup_instructions_tab(self):
        # Title with icon
        title_frame = ttk.Frame(self.instructions_frame, style="TFrame")
        title_frame.pack(fill=tk.X, pady=10)
        
        title_label = ttk.Label(
            title_frame, 
            text="🔍 How to Use This App", 
            style="Header.TLabel"
        )
        title_label.pack(pady=10)

        # Instructions text with custom styling
        instructions = """Welcome to the AI Ethics Advisor!

This application helps you learn ethics with responses in Hinglish or English.

📌 HOW TO USE:

1️⃣ Type your question about ethics and press Enter or click Send
   Example: "Data privacy ke baare mein batao" or "Explain major scales"

2️⃣ The AI will respond with helpful information tailored to your query

3️⃣ For better answers, try asking specific questions
   Example: "What is the difference between a major and minor chord?"
   
4️⃣ You can ask for examples, exercises, or explanations
   Example: "Can you give me some ear training exercises?"

✨ TIPS:
• Ask about any ethics topic - Western or Indian classical
• Request examples to understand concepts better
• Try asking for practice exercises

This application uses Google's Gemini AI to provide responses. Happy learning! 🧠

Developed by: """ + self.owner

        instruction_frame = ttk.Frame(self.instructions_frame, style="Secondary.TFrame")
        instruction_frame.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)
        
        instructions_text = scrolledtext.ScrolledText(
            instruction_frame, 
            wrap=tk.WORD, 
            width=80, 
            height=25, 
            font=("Helvetica", 10),
            bg=self.secondary_color,
            fg=self.text_color,
            relief=tk.FLAT
        )
        instructions_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        instructions_text.insert(tk.END, instructions)
        
        # Add some styling to the instructions
        instructions_text.tag_configure("title", foreground=self.accent_color, font=("Helvetica", 12, "bold"))
        instructions_text.tag_configure("subtitle", foreground=self.highlight_color, font=("Helvetica", 11, "bold"))
        instructions_text.tag_configure("tip", foreground=self.highlight_color, font=("Helvetica", 10, "italic"))
        
        instructions_text.config(state=tk.DISABLED)

    def send_question(self):
        question = self.question_input.get().strip()
        if not question:
            return

        self.question_input.delete(0, tk.END)
        self.question_input.config(state=tk.DISABLED)  # Disable input
        self.chat_display.config(state=tk.NORMAL)
        
        # Style the user message
        self.chat_display.insert(tk.END, "You: ", "user_prefix")
        self.chat_display.insert(tk.END, f"{question}\n\n", "user_message")
        
        # Configure tags for styling
        self.chat_display.tag_configure("user_prefix", foreground=self.accent_color, font=("Helvetica", 10, "bold"))
        self.chat_display.tag_configure("user_message", foreground=self.text_color, font=("Helvetica", 10))
        
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)

        self.status_var.set("🔄 Getting response...")

        # Check for app information questions before sending to API
        lower_question = question.lower()
        
        # Check for developer/team information questions
        if any(keyword in lower_question for keyword in ["who is your owner", "who made you", "who created you", 
                                                        "who developed you", "who is your developer", 
                                                        "who built you", "your developer", "your creator",
                                                        "who programmed you", "your owner"]):
            owner_response = f"I was developed by {self.owner}. I'm here to help you learn ethics!"
            self.response_queue.put(owner_response)
        # Check for "about" questions to show team details
        elif any(keyword in lower_question for keyword in ["about", "about this app", "about you", "team members", 
                                                          "developers", "creators", "team info", "team details",
                                                          "who made this app", "tell me about"]):
            team_info = "This app was developed by the following team members:\n\n"
            for member in self.team_members:
                team_info += f"• {member['name']} - {member['id']}\n"
            team_info += "\nThis application helps you learn ethics with responses in Hinglish or English."
            self.response_queue.put(team_info)
        else:
            threading.Thread(target=self.get_ai_response, args=(question,), daemon=True).start()

    def get_ai_response(self, prompt):
        """Get AI response in a separate thread with error handling"""
        try:
            # Enhance the prompt to ensure Hinglish responses when appropriate
            enhanced_prompt = f"""Please answer the following ethics question. If the question is in Hindi or contains Hindi words, 
            respond in Hinglish (mix of Hindi and English). If the question is in English, respond in English:
            
            {prompt}"""
            
            response = self.model.generate_content(enhanced_prompt)
            response_text = response.text if hasattr(response, 'text') else "Error: Unexpected response format"
        except Exception as e:
            response_text = f"Error: {str(e)}"

        self.response_queue.put(response_text)

    def update_chat_display(self, response):
        self.chat_display.config(state=tk.NORMAL)
        
        # Style the AI response
        self.chat_display.insert(tk.END, "AI: ", "ai_prefix")
        self.chat_display.insert(tk.END, f"{response}\n\n", "ai_message")
        
        # Configure tags for styling
        self.chat_display.tag_configure("ai_prefix", foreground=self.highlight_color, font=("Helvetica", 10, "bold"))
        self.chat_display.tag_configure("ai_message", foreground=self.text_color, font=("Helvetica", 10))
        
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
        self.status_var.set("✅ Ready")
        self.question_input.config(state=tk.NORMAL)  # Re-enable input

    def show_error(self, message):
        """Display error message in the chat window"""
        self.chat_display.config(state=tk.NORMAL)
        
        # Style the error message
        self.chat_display.insert(tk.END, "⚠️ Error: ", "error_prefix")
        self.chat_display.insert(tk.END, f"{message}\n\n", "error_message")
        
        # Configure tags for styling
        self.chat_display.tag_configure("error_prefix", foreground="#FF5252", font=("Helvetica", 10, "bold"))
        self.chat_display.tag_configure("error_message", foreground="#FF5252", font=("Helvetica", 10))
        
        self.chat_display.config(state=tk.DISABLED)
        self.status_var.set("❌ Error")


def main():
    root = tk.Tk()
    app = MusicTheoryTrainer(root)
    root.mainloop()


if __name__ == "__main__":
    main()
