# -*- coding: utf-8 -*-
import os
import sys
import requests
import random
import webbrowser
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QStackedWidget
from PyQt5.QtGui import QPixmap, QPalette, QBrush, QRegion, QPainterPath
from PyQt5.QtCore import Qt, QRectF

# TheMealDB API URL
API_URL = "https://www.themealdb.com/api/json/v1/1/filter.php?c={}"
DETAILS_URL = "https://www.themealdb.com/api/json/v1/1/lookup.php?i={}"

# Cuisine categories
CATEGORIES = ["Beef", "Chicken", "Dessert", "Lamb", "Miscellaneous", "Pasta", "Pork", "Seafood", "Side", "Starter", "Vegan", "Vegetarian", "Breakfast", "Goat"]

def resource_path(relative_path):
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, "Contents/Resources", relative_path)
        return os.path.join(os.path.abspath("."), relative_path)



class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setGeometry(0, 0, 450, 550)  # Set window size to match images
        self.setFixedSize(428, 512) #Prevent resize
        self.setStyleSheet("background: transparent;")
        
        self.update()
        self.repaint()
       

        self.old_pos = None    

        # Create stacked widget to switch between screens
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setFixedSize(450, 550)
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.stacked_widget)

        # Create screens
        self.start_screen = self.create_start_screen()
        self.cuisine_screen = self.create_cuisine_screen()
        self.meal_screen = self.create_meal_screen()

        # Add screens to stacked widget
        self.stacked_widget.addWidget(self.start_screen)
        self.stacked_widget.addWidget(self.cuisine_screen)
        self.stacked_widget.addWidget(self.meal_screen)

        # Show first screen
        self.stacked_widget.setCurrentWidget(self.start_screen)


    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        if self.old_pos is not None:
            delta = event.globalPos() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPos()

    def mouseReleaseEvent(self, event):
        self.old_pos = None

    
    def set_background(self, widget, image_path):
        """Ensure the window size matches the background image size."""
        
        full_path = resource_path(image_path)
        print(f"Trying to load image from: {full_path}")

        if not os.path.exists(full_path):
            print(f"ERROR: Image not found at {full_path}")
            return

        if not hasattr(widget, "bg_label"):
            widget.bg_label = QLabel(widget)

        pixmap = QPixmap(full_path)

        if pixmap.isNull():
            print(f"ERROR: Failed to load image: {full_path}")
        else:
            print(f"SUCCESS: Loaded image: {full_path}")

        # ✅ Automatically resize window to match image size
        self.setFixedSize(pixmap.width(), pixmap.height())

        # ✅ Resize QLabel to match new window size
        widget.bg_label.setGeometry(0, 0, self.width(), self.height())
        widget.bg_label.setPixmap(pixmap.scaled(self.width(), self.height(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation))
        widget.bg_label.lower()
        widget.bg_label.show()
            

        self.close_button = QPushButton("x", self)
        self.close_button.setGeometry(397, 21, 30, 30)
        self.close_button.setStyleSheet("background: #DFAF73; border-radius: 6px; font-size: 16px; colorblack;")
        self.close_button.clicked.connect(self.close)
        self.close_button.raise_()

        print(f"window size: {self.width()}x{self.height()}")
        print(f"Background QLabel size: {widget.bg_label.width()}x{widget.bg_label.height()}")
        





    def create_start_screen(self):
        """Create the start screen with the 'Begin' button."""
        screen = QWidget()
        self.set_background(screen, "screen1.png")  # Use provided background

        button = QPushButton("", screen)
        button.setGeometry(150, 255, 115, 50)  # Position over "Begin!" button
        button.setStyleSheet("background: transparent;")

        button.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.cuisine_screen))

        return screen

    def create_cuisine_screen(self):
        """Create the cuisine selection screen."""
        screen = QWidget()
        self.set_background(screen, "screen2.png")

        # Create cuisine buttons
        button_positions = {
            "Beef": (10, 70),
            "Pasta": (145, 70),
            "Seafood": (265, 70),
            "Chicken": (20, 190),
            "Side": (155, 190),
            "Starter": (275, 190),
            "Miscellaneous": (10, 285),
            "Vegan": (155, 285),
            "Breakfast": (265, 285),
            "Pork": (10, 390),
            "Vegetarian": (155, 390),
            "Dessert": (285, 390),
        }

        for cuisine, (x, y) in button_positions.items():
            button = QPushButton("", screen)
            button.setGeometry(x, y, 100, 50)  # Position over text
            button.setStyleSheet("background: transparent;")
            button.clicked.connect(lambda checked, c=cuisine: self.fetch_meal(c))

        return screen

    def create_meal_screen(self):
        """Create the meal display screen."""
        screen = QWidget()
        self.set_background(screen, "screen3.png")

        # Meal image
        self.meal_image = QLabel(screen)
        self.meal_image.setGeometry(70, 130, 300, 200)  # Position for meal image

        # Meal title
        self.meal_title = QLabel("Meal Title", screen)
        self.meal_title.setGeometry(70, 330, 300, 40)
        self.meal_title.setStyleSheet("font-size: 20px; font-weight: bold; color: white;")
        self.meal_title.setAlignment(Qt.AlignCenter)

        # View Recipe button
        self.recipe_button = QPushButton("", screen)
        self.recipe_button.setGeometry(85, 320, 230, 50)  # Position over "URL" text
        self.recipe_button.setStyleSheet("background: transparent;")

        self.recipe_button.clicked.connect(self.open_recipe)

        return screen

    def fetch_meal(self, cuisine):
        """Fetch a random meal from TheMealDB API based on selected cuisine."""
        response = requests.get(API_URL.format(cuisine))
        if response.status_code == 200:
            meals = response.json().get("meals", [])
            if meals:
                meal = random.choice(meals)  # Pick a random meal
                self.display_meal(meal["idMeal"], meal["strMeal"], meal["strMealThumb"])
        self.stacked_widget.setCurrentWidget(self.meal_screen)

    def display_meal(self, meal_id, meal_name, meal_image_url):
        """Display the selected meal on the meal screen."""
        self.meal_title.setText(meal_name)

        # Load meal image
        image_data = requests.get(meal_image_url).content
        pixmap = QPixmap()
        pixmap.loadFromData(image_data)
        self.meal_image.setPixmap(pixmap)
        self.meal_image.setScaledContents(True)

        # Store meal ID for opening recipe
        self.current_meal_id = meal_id

    def open_recipe(self):
        """Open the recipe URL in a web browser."""
        if hasattr(self, "current_meal_id"):
            response = requests.get(DETAILS_URL.format(self.current_meal_id))
            if response.status_code == 200:
                meal = response.json().get("meals", [])[0]
                webbrowser.open(meal["strSource"])  # Open recipe URL

# Run the application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    print("App is running...")
    sys.exit(app.exec_())
