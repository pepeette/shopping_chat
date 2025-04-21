# Water Filter Shopping Assistant

An intelligent shopping assistant that helps customers find the perfect water filtration solution based on their needs, preferences, and constraints.

## Features

- Conversational AI interface that asks users about their water filtration needs
- Personalized product recommendations based on installation type, budget, and filtration requirements
- Detailed product specifications and comparisons
- UK-focused pricing and availability information
- Open-source and easily extendable

## Installation

### Prerequisites

- Python 12 or newer
- Git (optional)

### Setup

1. Clone the repository (or download it):
   ```bash
   git clone https://github.com/your-username/water-filter-assistant.git
   cd water-filter-assistant
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. (Optional) Create a `.env` file with your Anthropic API key if you have one:
   ```
   ANTHROPIC_API_KEY=your_api_key_here
   ```
   Note: The application works without an API key using a mock AI service.

## Usage

Run the Streamlit application:

```bash
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`.

## How It Works

1. The user engages in a conversation with the assistant about their water filter needs
2. The assistant asks about installation preferences, budget, contaminant concerns, etc.
3. Once enough information is gathered, the system matches the requirements with available products
4. Top recommendations are presented with a comparison table and detailed specifications
5. Users can continue the conversation to refine requirements or ask questions

## Customizing Products

The product database is stored in `data/products.csv`. You can modify this file to add, remove, or update products.

Required columns:
- `product_id`: Unique identifier for the product
- `name`: Product name
- `type`: Product type (reverse_osmosis, countertop, pitcher, etc.)
- `price_gbp`: Price in Great British Pounds
- `installation`: Installation type
- (See file for complete column list)

## Deployment

### Streamlit Cloud (Free)

1. Push your code to GitHub
2. Go to [Streamlit Cloud](https://streamlit.io/cloud)
3. Connect your GitHub account
4. Select your repository and deploy

### Heroku (Free tier available)

1. Create a `Procfile` with the content:
   ```
   web: streamlit run app.py
   ```

2. Push to Heroku:
   ```bash
   heroku create water-filter-assistant
   git push heroku main
   ```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Inspired by [Anthropic's Claude](https://www.anthropic.com/claude)
