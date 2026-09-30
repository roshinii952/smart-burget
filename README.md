*PocketSmart AI* is a GenAI-powered, cross-platform recommendation system designed to provide personalized and budget-aware suggestions for products and services.

The system helps users plan and make decisions in three major areas:

* 🏠 Home Interior Planning
* 🎉 Party Planning
* 💎 Jewelry Selection

Users provide their budget, preferences, contextual requirements, and optionally an image. The AI analyzes these inputs and generates recommendations that are aligned with the user's requirements and financial limits.

The system is designed to bring multiple planning and purchasing needs into a single intelligent assistant. 

---

## 🎯 Problem Statement

Planning purchases and events within a fixed budget can be difficult because users often need to compare many products, services, platforms, prices, and options manually.

Traditional planning approaches require users to:

* Search across multiple platforms.
* Compare products and services manually.
* Allocate their budget themselves.
* Match products with their preferences and requirements.
* Find suitable jewelry based on an outfit or occasion.

These processes can be time-consuming and are not centralized into a single budgeting and recommendation workflow. 

---

## 💡 Proposed Solution

PocketSmart AI provides a centralized AI-powered recommendation assistant.

The user enters:

* Budget
* Preferences
* Category-specific requirements
* Contextual information
* Optional images for jewelry recommendations

The backend processes the information and sends the appropriate prompt to the Gemini AI layer. Gemini analyzes the input and generates domain-specific recommendations.

The system also supports user authentication, sessions, and recommendation history for personalized reuse. 

---

## 🎯 Objectives

The main objectives of PocketSmart AI are:

1. Provide personalized recommendations based on the user's budget and preferences.
2. Support Home Interior, Party, and Jewelry planning.
3. Use Gemini AI to understand text, numerical information, and optional images.
4. Connect recommendation workflows with multiple product and service platforms.
5. Provide a simple interface for entering requirements and reviewing recommendations.
6. Reduce the manual effort required for comparing products and services. 

---

## 🏗️ System Architecture

PocketSmart AI follows a modular architecture consisting of the following layers:

### Frontend

The frontend is developed using:

* HTML
* CSS
* JavaScript
* Jinja2 templates

It provides the user interface for entering budgets, preferences, planner details, and displaying AI-generated recommendations.

### Backend

The backend uses *FastAPI* to handle:

* API routes
* Request processing
* Authentication
* Sessions
* CORS
* Communication with the AI layer

### AI Layer

*Google Gemini 1.5 Flash Pro* acts as the core multimodal AI model.

It processes user text, numerical information, and optional images and generates personalized recommendations.

### Recommendation Layer

The recommendation layer connects the planning workflow with product and service sources.

### Main Modules

* Home Planner
* Party Planner
* Jewelry Planner
* User Authentication
* Session Management
* Recommendation History 

---

## 🧩 Main Modules

### 🏠 1. Home Interior Planner

The Home Planner allows users to provide their budget and room-related requirements.

It can generate recommendations related to:

* Furniture
* Décor
* Lighting
* Room requirements
* Quantities
* Interior planning

The backend provides a /generate-home endpoint for generating home interior recommendations. 

---

### 🎉 2. Party Planner

The Party Planner supports event-related planning.

Users can provide details such as:

* Budget
* Guest count
* Event type
* Venue requirements
* Catering requirements
* Decoration requirements

The system generates recommendations for areas such as:

* Food
* Venues
* Decorations

The backend provides a /generate-party endpoint. 

---

### 💎 3. Jewelry Planner

The Jewelry Planner provides personalized jewelry recommendations based on:

* Budget
* Occasion
* Style preferences
* Outfit requirements
* Optional outfit image

Gemini can analyze an uploaded outfit image for color coordination and aesthetics and generate suitable jewelry suggestions.

The backend provides a /generate-jewelry endpoint.  

---

## 🔐 User Authentication

PocketSmart AI includes user authentication and session management.

Supported authentication features include:

* User registration
* Login
* Logout
* JWT-based authorization
* Session management
* Session information
* Personalized recommendation history

Backend routes include:

* /register
* /login
* /logout
* /token
* /session-info
* /session-data 

---

## 🤖 Google Gemini Integration

Google Gemini is the core AI component of PocketSmart AI.

*Gemini 1.5 Flash Pro* is used to:

* Understand user requirements.
* Process budgets and numerical inputs.
* Analyze text.
* Process optional images.
* Generate personalized recommendations.
* Adapt recommendations according to different planning domains.

Separate prompt templates are used for:

* Home Planning
* Party Planning
* Jewelry Planning

For Jewelry Planner, the AI can analyze an uploaded outfit image to support color coordination and aesthetic recommendations. 

---

## 🔄 Working Process

The application works through the following workflow:

text
User
  ↓
Register / Login
  ↓
Select Planner
  ↓
Enter Budget & Preferences
  ↓
Enter Category-Specific Details
  ↓
Optional Image Upload
  ↓
FastAPI Backend
  ↓
Prepare AI Prompt
  ↓
Google Gemini
  ↓
Generate Recommendations
  ↓
Display Structured Results
  ↓
Save Recommendation History


The basic workflow consists of user authentication, planner selection, input collection, AI processing, recommendation generation, and history management. 

---

## 🛠️ Technologies Used

| Technology                  | Purpose                                 |
| --------------------------- | --------------------------------------- |
| Python                      | Backend programming                     |
| FastAPI                     | Backend framework and API development   |
| Google Gemini 1.5 Flash Pro | Generative AI and multimodal processing |
| HTML                        | Frontend structure                      |
| CSS                         | Frontend styling and responsive layout  |
| JavaScript                  | Dynamic frontend interaction            |
| Jinja2                      | Dynamic template rendering              |
| JWT                         | Authentication and authorization        |
| Sessions                    | User session management                 |
| Third-party platforms/APIs  | Product and service sourcing            |

Referenced product and service ecosystems include:

* Amazon
* Flipkart
* IKEA
* Swiggy
* Zomato
* OYO  

---

## 📁 Project Structure

text
PocketSmart-AI/
│
├── app.py / main.py
│
├── gemini_utils.py
│
├── templates/
│   └── index.html
│
├── static/
│   ├── style.css
│   └── script.js
│
├── requirements.txt
│
└── .env


### Backend

app.py or main.py handles:

* Application startup
* API routes
* Authentication
* Sessions
* CORS
* Communication with Gemini

### AI Utility Layer

gemini_utils.py handles:

* Prompt orchestration
* Budget formatting
* Domain segmentation
* Image analysis

### Frontend

index.html provides the planner interface.

style.css controls the visual design and responsive layout.

script.js handles:

* Form data collection
* API requests
* Backend responses
* Recommendation display

This modular structure supports the Home, Party, and Jewelry planning workflows. 

---

## ✨ Key Features

* 💰 Budget-aware recommendations
* 🎯 Personalized suggestions
* 🏠 Home interior planning
* 🎉 Party planning
* 💎 Jewelry recommendations
* 🖼️ Optional image-based jewelry analysis
* 🔐 User registration and login
* 🔑 JWT-based authorization
* 📊 Recommendation history
* 🤖 Gemini-powered AI recommendations
* 🌐 Multiple product/service platform references
* 📱 Responsive user interface
* 🔄 Session management 

---

## ▶️ How to Run

### 1. Set Up Python Environment

Create and activate a Python environment for the project.

### 2. Install Dependencies

Install the packages specified in:

text
requirements.txt


### 3. Configure Environment Variables

Configure the required Gemini API access and environment variables/API keys.

Example:

env
GEMINI_API_KEY=your_api_key_here


### 4. Start the Backend

Run the project's main Python application entry point:

bash
python app.py


or, depending on the project entry point:

bash
python main.py


### 5. Open the Application

Open the frontend/application in a web browser.

### 6. Use the Planner

Select one of:

* Home Interior
* Party
* Jewelry

Enter the required budget and preferences.

For Jewelry Planner, an outfit image can optionally be provided for image-based recommendations. 

---

## 📊 Expected Results

PocketSmart AI is designed to provide:

* Budget-based recommendations.
* Personalized suggestions based on user preferences.
* Context-aware planning.
* Image-based analysis for jewelry recommendations.
* Structured AI-generated recommendation results.
* User-specific recommendation history.
* Product and service sourcing across multiple platforms. 

---

## 🌟 Advantages

* Reduces manual product and service comparison.
* Combines multiple lifestyle planning categories into one application.
* Provides budget-aware recommendations.
* Supports both text and image inputs.
* Provides personalized recommendations.
* Uses a modular backend architecture.
* Maintains recommendation history for review and reuse. 

---

## 📱 Applications

PocketSmart AI can be applied to:

* Home interior and décor planning.
* Birthday event planning.
* Corporate event planning.
* Wedding event planning.
* Food and catering planning.
* Venue selection.
* Decoration planning.
* Occasion-based jewelry selection.
* Budget-conscious shopping and lifestyle planning. 

---

## 🚀 Future Enhancements

Future improvements planned for PocketSmart AI include:

1. Expand the number of supported product and service platforms.
2. Improve real-time product and service data integration.
3. Improve recommendation personalization using additional user history and preferences.
4. Add more lifestyle planning categories.
5. Enhance multimodal capabilities.
6. Optimize AI prompts and validation.
7. Improve fallback recommendations.
8. Improve scalability and security.
9. Further enhance UI/UX.  

---

## 🔮 Conclusion

*PocketSmart AI* combines *FastAPI, Google Gemini 1.5 Flash Pro, and a responsive web frontend* to create a budget-aware recommendation assistant.

The system brings Home Interior, Party, and Jewelry planning into a single personalized platform. By combining user budgets, preferences, contextual requirements, and optional image inputs, the application is designed to simplify everyday planning and reduce the effort involved in comparing products and services
