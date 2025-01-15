# AI-Powered Video Script Generator

## Overview

Welcome to the AI-Powered Video Script Generator! This web application enables users to craft AI-generated video scripts using the Hugging Face model. The application features a dynamic input field that supports uploading documents, images, and links to enhance the AI prompt, ensuring a seamless and interactive user experience.

## Objective

The goal of this project is to provide an intuitive platform for generating video scripts enriched with contextual data extracted from various user inputs. Initially designed to use the x.ai API, the application now leverages the Hugging Face model, offering greater flexibility and reliability without the need for external credits.

## Features

### Core Functionality

1. Dynamic Input Field:
    1. Enter a prompt as text.
    2. Upload files (e.g., .txt, .pdf) and parse them to extract meaningful text to enhance the prompt.
    3. Add external links to fetch metadata or text content (basic implementation).
2. AI Script Generation: Dynamically display the AI-generated script below the input field.
3. Responsive Design: Fully responsive application that works seamlessly on both mobile and desktop devices.

### File Handling

1. Extract and append text from uploaded files.
2. For images, external OCR APIs can be integrated to extract text.

### Save and Retrieve Scripts

1. Allow users to save generated scripts.
2. Provide a library to view previously saved scripts.

## Bonus Features

1. Pagination and Search: Implemented for the script library, enabling users to easily navigate and search through saved scripts.
2. Multi-Language Support: Generate scripts in different languages by selecting a language option.
3. Export Options: Download generated scripts as .txt or .pdf files.

## Tech Stack

1. Backend: Django
2. Frontend: HTML, TailwindCSS, JavaScript
3. AI Model: Hugging Face model

## Future Improvements

1. Implement the interactive file parsing feature for more granular control over uploaded content.
2. Explore additional integrations to enhance the user experience.

## Screenshot

![AI-Powered Video Script Generator](https://drive.google.com/uc?id=1n2AX8Ec3r6aDUILtgi6NN19oQ986j8Yx)
