# Mackney Gazette

A sophisticated AI-powered local newspaper simulation system that generates realistic articles, manages story continuations, and serves them through a modern web interface.

## Overview

The Mackney Gazette is a complete newspaper simulation platform that creates a fictional town called "Mackney" and generates realistic local news articles using OpenAI's GPT models. The system includes comprehensive town and population data generation, intelligent article creation with story continuations, and a responsive web interface for reading the generated content.

## Key Features

### 🏘️ **Town & Population Generation**
- **Realistic Town Data**: Generates comprehensive town infrastructure including streets, landmarks, businesses, parks, and schools
- **Demographic Simulation**: Creates detailed population data with realistic age distributions, occupations, income levels, and personality traits
- **Multi-locale Support**: Supports various locales (en_US, en_GB, etc.) for culturally appropriate content
- **Configurable Parameters**: Customizable town size, population scale, and characteristics

### 📰 **AI-Powered Article Generation**
- **Smart Content Creation**: Uses OpenAI GPT models to generate realistic newspaper articles across 10 categories
- **Story Continuations**: Intelligently creates follow-up articles for ongoing stories
- **Author Personas**: Features 10 unique journalist personas with distinct writing styles and specializations
- **Contextual Integration**: Articles incorporate actual town and population data for authenticity
- **Configurable Tone**: Supports various article tones from lighthearted to very serious

### 🌐 **Modern Web Interface**
- **Responsive Design**: Bootstrap-based responsive layout that works on all devices
- **Story Chain Navigation**: Intuitive navigation between related articles in a story series
- **Category Browsing**: Organized content by news categories with dedicated category pages
- **Professional Layout**: Clean, newspaper-style design with proper typography and spacing
- **Image Integration**: Support for article images with captions and credits

### ⚙️ **Automated Workflows**
- **Daily Article Generation**: Automated scripts for generating daily content
- **Story Management**: Intelligent tracking and continuation of ongoing stories
- **Data Persistence**: CSV-based article storage with backup capabilities
- **Article Pruning**: Configurable limits to maintain manageable dataset sizes

## Project Structure

```
mackney-gazette/
├── app/                          # Flask web application
│   ├── app.py                   # Main Flask application
│   ├── static/                  # CSS, JS, and images
│   └── templates/               # Jinja2 HTML templates
├── src/                         # Core Python modules
│   ├── generate_articles_daily.py  # Daily article generation script
│   ├── initialise_town.py       # Town initialization script
│   └── utils/
│       ├── data/                # Data generation modules
│       │   ├── generate_article.py  # Article content generation
│       │   ├── generate_town.py     # Town infrastructure generation
│       │   ├── generate_people.py   # Population data generation
│       │   └── *.yaml          # Configuration files
│       └── llm/                 # LLM integration
│           └── openai.py        # OpenAI API wrapper
├── data/                        # Generated data storage
│   ├── articles.csv            # Article database
│   ├── town_data.json         # Town infrastructure data
│   └── people_data.csv        # Population demographics
├── *.yaml                      # Configuration files
├── *.sh                        # Shell scripts for automation
└── requirements.txt            # Python dependencies
```

## Installation & Setup

### Prerequisites
- Python 3.8+
- OpenAI API key
- Virtual environment (recommended)

### 1. Clone and Setup Environment
```bash
git clone <repository-url>
cd mackney-gazette

# Create and activate virtual environment
python -m venv mackney-gazette-venv
source mackney-gazette-venv/bin/activate  # On Windows: mackney-gazette-venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure OpenAI API
Create a `credentials` file in the project root:
```json
{
  "openai_api_key": "your-openai-api-key-here"
}
```

Alternatively, set the environment variable:
```bash
export OPENAI_API_KEY="your-openai-api-key-here"
```

### 3. Initialize Town Data
```bash
# Initialize town and population data
./initialise_town.sh

# Or with custom configuration
python -m src.initialise_town --config custom_town_config.yaml
```

### 4. Generate Initial Articles
```bash
# Generate daily articles
./generate_articles_daily.sh

# Or with custom configuration
python -m src.generate_articles_daily --config custom_articles_config.yaml
```

### 5. Start the Web Server
```bash
# Start the Flask application
./run_website.sh

# Or manually
cd app
python app.py
```

Visit `http://localhost:5000` to view the Mackney Gazette website.

## Configuration

### Town Configuration (`town_init_config.yaml`)
```yaml
town:
  name: "Mackney"           # Town name
  size: "medium"            # small, medium, or large
  locale: "en_GB"           # Locale for content generation
  seed: 69                  # Random seed for reproducibility

newspaper:
  name: "Mackney Gazette"   # Newspaper name
  tagline: "Your Community, Your News"
  founded_year: 1883

population:
  scale_factor: 0.1         # Percentage of town population to generate
  min_people: 50           # Minimum number of people
```

### Article Generation (`articles_daily_config.yaml`)
```yaml
articles:
  count: 10                # Number of new articles per day
  story_continuation:
    count: 2               # Number of story continuations per day
    max_attempts: 5        # Max attempts to find eligible stories
  
  seriousness_weights:     # Distribution of article tones
    serious: 0.3
    balanced: 0.5
    light: 0.2
  
  save_options:
    backup_before_save: true
    article_limit: 100     # Maximum articles to keep (0 = unlimited)
```

## Usage

### Daily Operations
```bash
# Generate today's articles
./generate_articles_daily.sh

# Start/restart the website
./run_website.sh
```

### Advanced Usage
```bash
# Generate articles with custom configuration
python -m src.generate_articles_daily --config custom_config.yaml

# Initialize a new town
python -m src.initialise_town --config new_town_config.yaml

# Run Flask in development mode
cd app && flask run --debug
```

## Article Categories

The system generates articles across 10 news categories:
- **Politics** - Local government, elections, policy
- **Sports** - Local teams, events, athletics
- **Business** - Local commerce, economic news
- **Technology** - Tech developments, innovation
- **Health** - Medical news, public health
- **Education** - Schools, educational programs
- **Entertainment** - Arts, culture, events
- **Environment** - Environmental issues, climate
- **Crime** - Public safety, law enforcement
- **Local News** - Community events, general interest

## Story Continuations

The system intelligently manages ongoing stories:
- Tracks articles marked as "ongoing" vs "concluded"
- Generates follow-up articles with new developments
- Maintains story chains with proper navigation
- Configurable age limits for story eligibility (3-30 days)
- Category-specific continuation probabilities

## Author Personas

Features 10 unique journalist personas:
- **Sarah Johnson** - Political correspondent (analytical, authoritative)
- **Michael Chen** - Tech reporter (technical but accessible)
- **Jessica Rodriguez** - Investigative journalist (detailed, empathetic)
- **David Thompson** - Sports writer (conversational, colorful)
- **Emily Wilson** - Health reporter (clear, informative)
- **Robert Martinez** - Business expert (concise, data-driven)
- **Amanda Lee** - Arts critic (creative, opinionated)
- **Daniel Smith** - Environmental journalist (passionate, scientific)
- **Lisa Brown** - Education reporter (thoughtful, approachable)
- **James Wilson** - General assignment (straightforward, efficient)

## Data Structure

### Articles (`articles.csv`)
- **article_id**: Unique identifier (ART-YYYYMMDD format)
- **title**: Article headline
- **body**: Full article content
- **summary**: Brief article summary
- **publication_date**: Publication date (YYYY-MM-DD)
- **last_updated**: Last modification date (YYYY-MM-DD)
- **author**: Journalist name
- **category**: News category
- **status**: Article status (Draft/Published)
- **story_status**: Story completion status (ongoing/concluded)
- **parent_article_id**: Link to original story for continuations
- **images**: JSON array of image data

### Town Data (`town_data.json`)
- Basic town information (population, area, climate)
- Streets and infrastructure
- Landmarks and points of interest
- Businesses and commercial establishments
- Parks and recreational facilities
- Schools and educational institutions

### Population Data (`people_data.csv`)
- Personal information (name, age, gender)
- Demographics (education, employment, income)
- Contact information and addresses
- Personality traits and temperament
- Location within the town

## Technical Features

### Backend
- **Flask**: Modern Python web framework
- **Pandas**: Efficient data manipulation and CSV handling
- **OpenAI GPT**: Advanced natural language generation
- **Faker**: Realistic demographic data generation
- **YAML**: Human-readable configuration files

### Frontend
- **Bootstrap 5**: Responsive CSS framework
- **Font Awesome**: Professional icon library
- **Jinja2**: Powerful templating engine
- **Responsive Design**: Mobile-first approach

### Data Management
- **CSV Storage**: Simple, portable data format
- **JSON Configuration**: Human-readable settings
- **Automatic Backups**: Data safety measures
- **Data Pruning**: Automatic old article removal

## Automation & Scheduling

The system is designed for automated daily operation:

### Cron Job Example
```bash
# Add to crontab for daily article generation at 6 AM
0 6 * * * /path/to/mackney-gazette/generate_articles_daily.sh
```

### GitHub Actions (Example)
```yaml
name: Daily Article Generation
on:
  schedule:
    - cron: '0 6 * * *'  # Daily at 6 AM UTC
jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Generate Articles
        run: ./generate_articles_daily.sh
```

## Troubleshooting

### Common Issues

**OpenAI API Errors**
- Verify API key is correctly set
- Check API quota and billing
- Ensure stable internet connection

**No Articles Generated**
- Check OpenAI API configuration
- Verify town and people data exist
- Review configuration file syntax

**Website Not Loading**
- Ensure Flask dependencies are installed
- Check that port 5000 is available
- Verify articles.csv exists in data directory

**Story Continuations Not Working**
- Ensure articles exist with "ongoing" status
- Check story age limits in configuration
- Verify parent_article_id relationships

### Development Mode
```bash
# Run with debug output
export FLASK_ENV=development
cd app && python app.py

# Generate articles with verbose output
python -m src.generate_articles_daily --config articles_daily_config.yaml
```

## Contributing

The project is designed for easy extension and customization:

1. **Add New Categories**: Modify `article_config.yaml`
2. **Create New Authors**: Extend the authors section in configuration
3. **Customize Town Types**: Modify town generation parameters
4. **Extend Data Models**: Add new fields to CSV structures
5. **Enhance UI**: Modify templates and CSS in the app directory

## License

This project is designed for educational and demonstration purposes. Please ensure compliance with OpenAI's usage policies when using their API.

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review configuration files for proper syntax
3. Ensure all dependencies are installed
4. Verify OpenAI API access and quotas

---

**The Mackney Gazette** - Demonstrating the power of AI-generated content in a realistic newspaper simulation environment.
