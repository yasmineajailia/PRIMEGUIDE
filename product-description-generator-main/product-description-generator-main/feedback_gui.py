import tkinter as tk
from tkinter import messagebox


def save_feedback(rating):
    # Save feedback to a text file
    with open("feedback.txt", "a") as f:
        f.write(f"Feedback: {rating} stars\n")
    # Display a message in the GUI
    messagebox.showinfo(
        "Thank you", f"Your feedback ({rating} stars) has been recorded!"
    )
    # Display feedback in the terminal
    print(f"You gave {rating} stars.")


def feedback_window():
    # Create main window
    window = tk.Tk()
    window.title("Star Feedback")
    window.geometry("400x300")
    window.configure(bg="#f0f0f0")  # Background color

    # Title
    label = tk.Label(
        window, text="Give your feedback:", font=("Arial", 16), bg="#f0f0f0"
    )
    label.pack(pady=10)

    # Label to display selected feedback
    selected_feedback = tk.StringVar()
    selected_feedback.set("No feedback selected.")
    feedback_label = tk.Label(
        window, textvariable=selected_feedback, font=("Arial", 12), bg="#f0f0f0"
    )
    feedback_label.pack(pady=10)

    # Star buttons
    def update_feedback(rating):
        selected_feedback.set(f"You selected {rating} stars.")
        save_feedback(rating)

    for i in range(1, 6):
        button = tk.Button(
            window,
            text="★" * i,
            font=("Arial", 18),
            bg="#ffcc00",
            activebackground="#ffd700",
            command=lambda rating=i: update_feedback(rating),
        )
        button.pack(pady=5)

    # Cancel button
    cancel_button = tk.Button(
        window,
        text="Cancel",
        font=("Arial", 12),
        bg="#ff6666",
        activebackground="#ff4d4d",
        command=window.destroy,
    )
    cancel_button.pack(pady=20)

    # Start main loop
    window.mainloop()


# Test the interface
if __name__ == "__main__":
    feedback_window()
