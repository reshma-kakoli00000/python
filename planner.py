import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from tkinter import font as tkFont
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import json
import os

class ShoppingListApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Household Planner")
        self.users = {}  # Stores user accounts
        self.current_user = None  # Tracks the currently logged-in user
        self.shopping_lists = {}  # Stores all shopping lists for the current user

        # Predefined categories
        self.categories = ["Groceries", "Utilities", "Entertainment", "Transport", "Health", "Other"]

        # Load saved data (if any)
        self.load_data()

        # Set up fonts and colors
        self.title_font = tkFont.Font(family="Helvetica", size=18, weight="bold")
        self.label_font = tkFont.Font(family="Helvetica", size=12)
        self.button_font = tkFont.Font(family="Helvetica", size=12, weight="bold")
        self.bg_color = "#f5f5f5"
        self.button_color = "#0078D7"  # A modern blue color
        self.button_text_color = "white"
        self.listbox_bg = "white"
        self.listbox_fg = "black"
        self.warning_color = "red"  # Color for budget exceed warning

        # Configure root window
        self.root.configure(bg=self.bg_color)
        self.root.geometry("600x400")  # Set a fixed window size

        # Bind the closing event to save data
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Show login screen
        self.show_login_screen()

    def show_login_screen(self):
        """Display the login/signup screen."""
        self.clear_frame()

        self.login_frame = ttk.Frame(self.root, padding="20")
        self.login_frame.grid(row=0, column=0, sticky="nsew")
        self.login_frame.place(relx=0.5, rely=0.5, anchor="center")  # Center the frame

        # Title Label
        self.title_label = ttk.Label(
            self.login_frame, text="Smart Household Planner", font=self.title_font, background=self.bg_color
        )
        self.title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # Username Entry
        self.username_label = ttk.Label(self.login_frame, text="Username:", font=self.label_font, background=self.bg_color)
        self.username_label.grid(row=1, column=0, pady=5)
        self.username_entry = ttk.Entry(self.login_frame, width=30, font=self.label_font)
        self.username_entry.grid(row=1, column=1, pady=5)

        # Password Entry
        self.password_label = ttk.Label(self.login_frame, text="Password:", font=self.label_font, background=self.bg_color)
        self.password_label.grid(row=2, column=0, pady=5)
        self.password_entry = ttk.Entry(self.login_frame, width=30, font=self.label_font, show="*")
        self.password_entry.grid(row=2, column=1, pady=5)

        # Buttons
        self.login_button = ttk.Button(
            self.login_frame, text="Login", command=self.login, style="Accent.TButton"
        )
        self.login_button.grid(row=3, column=0, pady=10, padx=5, sticky="ew")

        self.signup_button = ttk.Button(
            self.login_frame, text="Sign Up", command=self.signup, style="Accent.TButton"
        )
        self.signup_button.grid(row=3, column=1, pady=10, padx=5, sticky="ew")

    def login(self):
        """Handle user login."""
        username = self.username_entry.get()
        password = self.password_entry.get()

        if username in self.users and self.users[username]["password"] == password:
            self.current_user = username
            self.shopping_lists = self.users[username]["shopping_lists"]
            self.show_main_screen()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

    def signup(self):
        """Handle user signup."""
        username = self.username_entry.get()
        password = self.password_entry.get()

        if username in self.users:
            messagebox.showerror("Signup Failed", "Username already exists.")
        elif username and password:
            self.users[username] = {"password": password, "shopping_lists": {}}
            self.current_user = username
            self.shopping_lists = self.users[username]["shopping_lists"]
            self.show_main_screen()
        else:
            messagebox.showerror("Signup Failed", "Please enter a username and password.")

    def show_main_screen(self):
        """Display the main screen after login."""
        self.clear_frame()

        self.main_frame = ttk.Frame(self.root, padding="20")
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        self.main_frame.place(relx=0.5, rely=0.5, anchor="center")  # Center the frame

        # Title Label
        self.title_label = ttk.Label(
            self.main_frame, text="Smart Household Planner", font=self.title_font, background=self.bg_color
        )
        self.title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # Listbox for shopping lists
        self.listbox = tk.Listbox(
            self.main_frame, width=50, height=10, font=self.label_font, bg=self.listbox_bg, fg=self.listbox_fg
        )
        self.listbox.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

        # Buttons
        self.add_list_button = ttk.Button(
            self.main_frame,
            text="Add New List",
            command=self.add_new_list,
            style="Accent.TButton",
        )
        self.add_list_button.grid(row=2, column=0, pady=10, padx=5, sticky="ew")

        self.open_list_button = ttk.Button(
            self.main_frame,
            text="Open Selected List",
            command=self.open_selected_list,
            style="Accent.TButton",
        )
        self.open_list_button.grid(row=2, column=1, pady=10, padx=5, sticky="ew")

        self.delete_list_button = ttk.Button(
            self.main_frame,
            text="Delete Selected List",
            command=self.delete_selected_list,
            style="Accent.TButton",
        )
        self.delete_list_button.grid(row=3, column=0, columnspan=2, pady=10, padx=5, sticky="ew")

        # Logout Button
        self.logout_button = ttk.Button(
            self.main_frame,
            text="Logout",
            command=self.logout,
            style="Accent.TButton",
        )
        self.logout_button.grid(row=4, column=0, columnspan=2, pady=10, padx=5, sticky="ew")

        # Update listbox with saved data
        self.update_listbox()

    def logout(self):
        """Handle user logout."""
        self.save_data()  # Save data before logging out
        self.current_user = None
        self.shopping_lists = {}
        self.show_login_screen()

    def add_new_list(self):
        list_name = simpledialog.askstring("New List", "Enter a name for the new shopping list:")
        if list_name and list_name not in self.shopping_lists:
            self.shopping_lists[list_name] = {"items": [], "budget": 0, "spent": 0, "categories": {}}
            self.update_listbox()
        elif list_name in self.shopping_lists:
            messagebox.showwarning("Duplicate", "A list with this name already exists!")

    def open_selected_list(self):
        selected = self.listbox.curselection()
        if selected:
            list_name = self.listbox.get(selected)
            self.open_list_window(list_name)

    def delete_selected_list(self):
        selected = self.listbox.curselection()
        if selected:
            list_name = self.listbox.get(selected)
            del self.shopping_lists[list_name]
            self.update_listbox()

    def update_listbox(self):
        self.listbox.delete(0, tk.END)
        for list_name in self.shopping_lists:
            self.listbox.insert(tk.END, list_name)

    def open_list_window(self, list_name):
        list_window = tk.Toplevel(self.root)
        list_window.title(f"Shopping List: {list_name}")
        list_window.configure(bg=self.bg_color)
        list_window.geometry("600x600")  # Set a fixed window size

        # Frame for items
        items_frame = ttk.Frame(list_window, padding="20")
        items_frame.grid(row=0, column=0, sticky="nsew")
        items_frame.place(relx=0.5, rely=0.5, anchor="center")  # Center the frame

        # Listbox for items
        self.items_listbox = tk.Listbox(
            items_frame, width=50, height=10, font=self.label_font, bg=self.listbox_bg, fg=self.listbox_fg
        )
        self.items_listbox.grid(row=0, column=0, columnspan=2, padx=5, pady=5)

        # Entry for new item
        self.new_item_entry = ttk.Entry(items_frame, width=30, font=self.label_font)
        self.new_item_entry.grid(row=1, column=0, padx=5, pady=5)

        # Entry for item price
        self.new_item_price_entry = ttk.Entry(items_frame, width=10, font=self.label_font)
        self.new_item_price_entry.grid(row=1, column=1, padx=5, pady=5)

        # Dropdown for item category
        self.category_var = tk.StringVar()
        self.category_dropdown = ttk.Combobox(items_frame, textvariable=self.category_var, values=self.categories, width=15, font=self.label_font)
        self.category_dropdown.grid(row=1, column=2, padx=5, pady=5)
        self.category_dropdown.current(0)  # Set default category

        # Add Item Button (with dynamic text)
        self.add_item_button = ttk.Button(
            items_frame, text="Add Item", command=lambda: self.add_item(list_name), style="Accent.TButton"
        )
        self.add_item_button.grid(row=2, column=0, pady=10, padx=5, sticky="ew")

        # Update button text when entry fields change
        self.new_item_entry.bind("<KeyRelease>", lambda event: self.update_add_item_button(list_name))
        self.new_item_price_entry.bind("<KeyRelease>", lambda event: self.update_add_item_button(list_name))

        # Remove Selected Item Button
        remove_item_button = ttk.Button(
            items_frame, text="Remove Selected Item", command=lambda: self.remove_item(list_name), style="Accent.TButton"
        )
        remove_item_button.grid(row=2, column=1, pady=10, padx=5, sticky="ew")

        # Mark as Purchased Button
        purchase_item_button = ttk.Button(
            items_frame, text="Mark as Purchased", command=lambda: self.purchase_item(list_name), style="Accent.TButton"
        )
        purchase_item_button.grid(row=3, column=0, columnspan=2, pady=10, padx=5, sticky="ew")

        # Modify Budget Button
        modify_budget_button = ttk.Button(
            items_frame, text="Modify Budget", command=lambda: self.modify_budget(list_name), style="Accent.TButton"
        )
        modify_budget_button.grid(row=4, column=0, columnspan=2, pady=10, padx=5, sticky="ew")

        # Export List Button
        export_list_button = ttk.Button(
            items_frame, text="Export List", command=lambda: self.export_list(list_name), style="Accent.TButton"
        )
        export_list_button.grid(row=5, column=0, columnspan=2, pady=10, padx=5, sticky="ew")

        # Back Button
        back_button = ttk.Button(
            items_frame, text="Back", command=list_window.destroy, style="Accent.TButton"
        )
        back_button.grid(row=6, column=0, columnspan=2, pady=10, padx=5, sticky="ew")

        # Budget Labels
        self.budget_label = ttk.Label(
            items_frame, text=f"Budget: ${self.shopping_lists[list_name]['budget']:.2f}", font=self.label_font, background=self.bg_color
        )
        self.budget_label.grid(row=7, column=0, columnspan=2, pady=5)

        self.spent_label = ttk.Label(
            items_frame, text=f"Spent: ${self.shopping_lists[list_name]['spent']:.2f}", font=self.label_font, background=self.bg_color
        )
        self.spent_label.grid(row=8, column=0, columnspan=2, pady=5)

        self.remaining_label = ttk.Label(
            items_frame,
            text=f"Remaining: ${self.shopping_lists[list_name]['budget'] - self.shopping_lists[list_name]['spent']:.2f}",
            font=self.label_font,
            background=self.bg_color,
        )
        self.remaining_label.grid(row=9, column=0, columnspan=2, pady=5)

        # Budget Exceed Warning Label
        self.exceed_warning_label = ttk.Label(
            items_frame, text="", font=self.label_font, background=self.bg_color, foreground=self.warning_color
        )
        self.exceed_warning_label.grid(row=10, column=0, columnspan=2, pady=5)

        # Pie Chart Button
        pie_chart_button = ttk.Button(
            items_frame, text="Show Spending Breakdown", command=lambda: self.show_pie_chart(list_name), style="Accent.TButton"
        )
        pie_chart_button.grid(row=11, column=0, columnspan=2, pady=10, padx=5, sticky="ew")

        self.update_items_listbox(list_name)

    def update_add_item_button(self, list_name):
        """Update the 'Add Item' button text with the current item name and price."""
        item_name = self.new_item_entry.get()
        item_price = self.new_item_price_entry.get()
        if item_name and item_price:
            self.add_item_button.config(text=f"Add Item: {item_name} - ${item_price}")
        else:
            self.add_item_button.config(text="Add Item")

    def add_item(self, list_name):
        item_name = self.new_item_entry.get()
        item_price = self.new_item_price_entry.get()
        item_category = self.category_var.get()

        if item_name and item_price:
            try:
                item_price = float(item_price)
                if item_name not in [item[0] for item in self.shopping_lists[list_name]["items"]]:
                    self.shopping_lists[list_name]["items"].append((item_name, item_price, False, item_category))  # (name, price, purchased, category)
                    self.update_items_listbox(list_name)
                    self.new_item_entry.delete(0, tk.END)
                    self.new_item_price_entry.delete(0, tk.END)
                    self.category_dropdown.current(0)  # Reset category dropdown
                    self.update_add_item_button(list_name)  # Reset button text
                else:
                    messagebox.showwarning("Duplicate", "This item already exists in the list!")
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter a valid price!")
        else:
            messagebox.showwarning("Missing Input", "Please enter both item name and price!")

    def remove_item(self, list_name):
        selected = self.items_listbox.curselection()
        if selected:
            item_index = selected[0]
            del self.shopping_lists[list_name]["items"][item_index]
            self.update_items_listbox(list_name)

    def purchase_item(self, list_name):
        selected = self.items_listbox.curselection()
        if selected:
            item_index = selected[0]
            item = self.shopping_lists[list_name]["items"][item_index]
            if not item[2]:  # If not already purchased
                self.shopping_lists[list_name]["items"][item_index] = (item[0], item[1], True, item[3])  # Mark as purchased
                self.update_items_listbox(list_name)

    def modify_budget(self, list_name):
        """Allow the user to modify the initial budget."""
        new_budget = simpledialog.askfloat("Modify Budget", f"Enter the new budget for '{list_name}':")
        if new_budget is not None:
            self.shopping_lists[list_name]["budget"] = new_budget
            self.update_items_listbox(list_name)

    def export_list(self, list_name):
        """Export the shopping list to a text file."""
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
        if file_path:
            with open(file_path, "w") as file:
                file.write(f"Shopping List: {list_name}\n")
                file.write(f"Budget: ${self.shopping_lists[list_name]['budget']:.2f}\n")
                file.write(f"Spent: ${self.shopping_lists[list_name]['spent']:.2f}\n")
                file.write(f"Remaining: ${self.shopping_lists[list_name]['budget'] - self.shopping_lists[list_name]['spent']:.2f}\n\n")
                file.write("Items:\n")
                for item in self.shopping_lists[list_name]["items"]:
                    status = "Purchased" if item[2] else "Not Purchased"
                    file.write(f"{item[0]} - ${item[1]:.2f} - {status} - Category: {item[3]}\n")
            messagebox.showinfo("Export Successful", f"Shopping list exported to {file_path}")

    def update_items_listbox(self, list_name):
        self.items_listbox.delete(0, tk.END)
        for item in self.shopping_lists[list_name]["items"]:
            status = "Purchased" if item[2] else "Not Purchased"
            self.items_listbox.insert(tk.END, f"{item[0]} - ${item[1]:.2f} - {status} - Category: {item[3]}")

        # Update budget labels
        total_spent = sum(item[1] for item in self.shopping_lists[list_name]["items"] if item[2])
        self.shopping_lists[list_name]["spent"] = total_spent
        self.budget_label.config(text=f"Budget: ${self.shopping_lists[list_name]['budget']:.2f}")
        self.spent_label.config(text=f"Spent: ${total_spent:.2f}")
        remaining = self.shopping_lists[list_name]["budget"] - total_spent
        self.remaining_label.config(text=f"Remaining: ${remaining:.2f}")

        # Check if budget is exceeded
        if remaining < 0:
            self.exceed_warning_label.config(text=f"Budget Exceeded by: ${-remaining:.2f}")
        else:
            self.exceed_warning_label.config(text="")

    def show_pie_chart(self, list_name):
        purchased_items = [item for item in self.shopping_lists[list_name]["items"] if item[2]]
        not_purchased_items = [item for item in self.shopping_lists[list_name]["items"] if not item[2]]

        purchased_total = sum(item[1] for item in purchased_items)
        not_purchased_total = sum(item[1] for item in not_purchased_items)

        labels = ["Purchased", "Not Purchased"]
        sizes = [purchased_total, not_purchased_total]

        fig, ax = plt.subplots()
        ax.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=90)
        ax.axis("equal")  # Equal aspect ratio ensures the pie chart is circular.

        # Embed the pie chart in the Tkinter window
        pie_chart_window = tk.Toplevel(self.root)
        pie_chart_window.title("Spending Breakdown")
        canvas = FigureCanvasTkAgg(fig, master=pie_chart_window)
        canvas.draw()
        canvas.get_tk_widget().pack()

    def clear_frame(self):
        """Clear the current frame."""
        for widget in self.root.winfo_children():
            widget.destroy()

    def load_data(self):
        """Load user data from a JSON file."""
        try:
            if os.path.exists("users.json"):
                with open("users.json", "r") as file:
                    self.users = json.load(file)
                    print("Data loaded successfully.")
        except Exception as e:
            print(f"Error loading data: {e}")

    def save_data(self):
        """Save user data to a JSON file."""
        try:
            with open("users.json", "w") as file:
                json.dump(self.users, file)
                print("Data saved successfully.")
        except Exception as e:
            print(f"Error saving data: {e}")

    def on_closing(self):
        """Save data and close the application."""
        self.save_data()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ShoppingListApp(root)
    root.mainloop()