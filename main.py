import tkinter as tk
import tkinter.messagebox as msgbox
import tkinter.simpledialog as simpledialog
import tkinter.filedialog as filedialog
import os
import shutil
import requests
import subprocess
import webbrowser

'''
    Create a UI interface that will let me manage instances of my discord bots and their custom settings.
        - Have a list of all available cogs listed on the left side of the window, read from the cogs folder.
        - Have a list of all current instances of the bot using a new folder for every instance.
            - Each folder will have the same base file structure, but with different cogs in the cogs folder.
        - Have a universal .env file that can host all the tokens and the client ids for the bots.
        - Allow me to create an invite link directly from the UI, and copy it to my clipboard.
            - This will be done by using the client id and the permissions integer, using a base link and formatting it.
        - Allow me to create a new instance of the bot, and have it create a new folder with the same base file structure.
            - This will be done by copying the base folder and renaming it.
        - Allow me to delete an instance of the bot, and have it delete the folder.
            - This will be done by deleting the folder.
        - Allow for a button to refresh the lists

'''

class BotManager(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Discord Bot Manager")
        self.geometry("800x400")
        self.resizable(True, True)

        # Create the base folder structure
        if not os.path.exists("instances"):
            os.makedirs("instances")
        if not os.path.exists("base_folder"):
            os.makedirs("base_folder")
            os.makedirs(os.path.join("base_folder", "cogs"))
        
        # Create the base .env file
        if not os.path.exists(".env"):
            with open(".env", "w") as f:
                f.write("TOKEN")
        
        # Copy the .env to the base folder
        if not os.path.exists(os.path.join("base_folder", ".env")):
            shutil.copyfile(".env", os.path.join("base_folder", ".env"))
        
        # UI Elements
        self.menu_bar = tk.Menu(self)
        self.config(menu=self.menu_bar)

        # File Menu
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Refresh Lists", command=self.refresh_lists)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.destroy)

        # About Menu
        self.about_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="About", menu=self.about_menu)
        self.about_menu.add_command(label="Help", command=self.aboutMenu)
        self.about_menu.add_separator()
        self.about_menu.add_command(label="Github", command=self.open_github)
        self.about_menu.add_command(label="Discord", command=self.open_discord_serverinvite)

        self.instance_list = tk.Listbox(self, width=30, height=10)
        self.instance_list.place(x=10, y=10)
        
        self.cog_list = tk.Listbox(self, width=30, height=10)
        self.cog_list.place(x=10, y=200)
# 
        # self.create_instance_button = tk.Button(self, text="Create Instance", command=self.create_instance)
        # self.create_instance_button.pack(side="left", padx=10, pady=20)
# 
        # self.delete_instance_button = tk.Button(self, text="Delete Instance", command=self.delete_instance)
        # self.delete_instance_button.pack(side="left", padx=15, pady=20)
# 
        # self.open_instance_button = tk.Button(self, text="Open Folder in Explorer", command=self.open_instance)
        # self.open_instance_button.pack(side="left", padx=20, pady=20)
# 
        # self.create_invite_button = tk.Button(self, text="Create Invite", command=self.create_invite)
        # self.create_invite_button.pack(side="left", padx=25, pady=20)
# 
        # self.update_env_button = tk.Button(self, text="Update .env", command=self.update_env)
        # self.update_env_button.pack(side="left", padx=30, pady=20)
# 
        # self.refresh_lists_button = tk.Button(self, text="Refresh Lists", command=self.refresh_lists)
        # self.refresh_lists_button.pack(side="left", padx=35, pady=20)
# 
        # self.upload_github = tk.Button(self, text="Upload to Github", command=self.upload_github)
        # self.upload_github.pack(side="left", padx=40, pady=20)

        self.populate_cog_list()
        self.populate_instance_list()


    def aboutMenu(self):
        pass

    def open_instance(self):
        # Open the folder of the selected instance in the explorer.
        index = self.instance_list.curselection()[0]
        folder = self.instance_list.get(index)
        subprocess.Popen(f'explorer "{os.path.join("instances", folder)}"')
    
    def populate_cog_list(self):
        self.cog_list.insert(tk.END, "Cogs")
        # Populate the cog list with all the cogs in the cogs folder. This will be done by reading the folder and adding each file to the list.
        for file in os.listdir("cogs"):
            self.cog_list.insert(tk.END, file)

    def populate_instance_list(self):
        self.instance_list.insert(tk.END, "Instances")
        # Populate the instance list with all the instances in the instances folder. This will be done by reading the folder and adding each folder to the list.
        for folder in os.listdir("instances"):
            self.instance_list.insert(tk.END, folder)
    
    def open_folder(self, event):
        index = self.instance_list.curselection()[0]
        folder_name = self.instance_list.get(index)
        folder_path = os.path.join("instances", folder_name)
        if os.path.isdir(folder_path):
            subprocess.run(["explorer", folder_path])

    def create_instance(self):
        base_folder = "base_folder"
        new_instance_name = simpledialog.askstring("New Instance", "Enter the name of the new instance.", initialvalue = "New Bot Instance")
        new_instance_folder = os.path.join("instances", new_instance_name)
        os.makedirs(new_instance_folder)
        for file in os.listdir(base_folder):
            s = os.path.join(base_folder, file)
            d = os.path.join(new_instance_folder, file)
            if os.path.isdir(s):
                shutil.copytree(s, d)
            else:
                shutil.copy2(s, d)
        self.refresh_lists()
        msgbox.showinfo(f"Instance {new_instance_name} Creation Success", f"Instance created successfully. You can now edit the files in folder {new_instance_name}.")
    
    def delete_instance(self):
        # Delete an instance folder from the instances folder.
        # This will be done by using the filedialog to select a folder, and then using the shutil module to delete it.
        selected_folder = filedialog.askdirectory(initialdir="instances", title="Select folder to delete")
        result = tk.messagebox.askquestion("Delete folder", f"Are you sure you want to delete {selected_folder}?", icon='warning')
        if result == 'yes':
            shutil.rmtree(selected_folder)
            self.refresh_lists()
            msgbox.showinfo("Folder Deletion Success", f"Folder {selected_folder} deleted successfully.")

    def create_invite(self):
        # Create an invite link directly from the UI, and copy it to my clipboard.
        # This will be done by using the client id and the permissions integer, using a base link and formatting it.
        pass

    def update_env(self):
        # Update the .env file with the new tokens and client ids.
        # This will be done by reading the .env file and replacing the tokens and client ids with the new ones.
        pass
    
    def refresh_lists(self):
        # Refresh the lists
        # This will be done by clearing the lists and repopulating them.
        self.cog_list.delete(0, tk.END)
        self.instance_list.delete(0, tk.END)
        self.populate_cog_list()
        self.populate_instance_list()

    def open_github(self):
        # Open the github repo in the browser.
        # This will be done by using the webbrowser module to open the link.
        webbrowser.open("https://www.github.com/snoopee110")

    def upload_github(self):
        # Upload the code to github.
        # This will be done by using the git module to push the code.
        pass
    
    def open_discord_serverinvite(self):
        # Open the discord server invite in the browser.
        # This will be done by using the webbrowser module to open the link.
        webbrowser.open("https://discord.com/") # TODO: Add the invite link here.


if __name__ == "__main__":
    app = BotManager()
    app.mainloop()
