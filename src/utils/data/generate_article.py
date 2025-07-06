"""
Module for generating mock news articles for the Mackney Gazette.
"""
import os
import yaml
import json
import random
import datetime
import pandas as pd
import httpx
import time
from pathlib import Path
from typing import Dict, Any, List, Optional

from src.utils.llm.openai import call_openai_api

def load_config(config_file):
    """
    Load configuration from YAML file.
    
    Args:
        config_file: Path to the YAML configuration file
        
    Returns:
        Dict containing configuration data
    """
    with open(config_file, 'r') as file:
        return yaml.safe_load(file)

def load_town_data(file_path):
    """
    Load town data from a JSON file.
    
    Args:
        file_path: Path to the town data JSON file
        
    Returns:
        Dict containing town data
    """
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading town data: {e}")
        return {}
        
def load_people_data(file_path):
    """
    Load people data from a CSV file.
    
    Args:
        file_path: Path to the people data CSV file
        
    Returns:
        DataFrame containing people data
    """
    try:
        return pd.read_csv(file_path)
    except Exception as e:
        print(f"Error loading people data: {e}")
        return pd.DataFrame()

def generate_article_content(
    category: str,
    author_info: Dict[str, Any],
    article_town_data: Dict[str, Any] = None,
    article_people_data: List[Dict[str, Any]] = None,
    seriousness: str = "balanced",
    config: Dict[str, Any] = None
) -> Dict[str, str]:
    """
    Generate article title, body, and summary using the OpenAI API.
    
    Args:
        category: The article category (e.g., Politics, Sports)
        author_info: Information about the author including name, persona, and writing style
        article_town_data: Optional town data to include in the article
        article_people_data: Optional list of people data to include in the article
        seriousness: The tone of the article from very_lighthearted to very_serious
        config: Configuration data loaded from article_config.yaml
        
    Returns:
        Dictionary containing the generated title, body, and summary
    """
    print("\n=== GENERATING ARTICLE CONTENT WITH OPENAI ===")
    
    # If config is not provided, load it
    if config is None:
        current_dir = Path(__file__).parent
        config_file = current_dir / 'article_config.yaml'
        config = load_config(config_file)
    
    # Get prompt templates from config
    prompt_templates = config.get('prompts', {})
    
    # Get tone description from config
    tone_descriptions = prompt_templates.get('tone_descriptions', {})
    tone_description = tone_descriptions.get(seriousness, tone_descriptions.get("balanced", "with a balanced tone"))
    
    # Create system prompt using template from config
    system_prompt_template = prompt_templates.get('system_prompt', '')
    system_prompt = system_prompt_template.format(
        author_name=author_info['name'],
        author_persona=author_info['persona'],
        author_style=author_info.get('writing_style', 'professional'),
        category=category,
        tone_description=tone_description
    )
    
    # Build town context string
    town_context = ""
    if article_town_data and article_town_data.get('town_name'):
        town_context += f"The article should be set in {article_town_data['town_name']}, "
        town_context += f"a town with a population of {article_town_data.get('town_population', 'unknown')}. "
        town_context += "there is no need to mention the town's name in the article body, but it should be clear where the article is set for example you can use the street names."
        
        # Add featured streets if available
        if 'town_features' in article_town_data and 'streets' in article_town_data['town_features']:
            streets = article_town_data['town_features']['streets']
            if streets:
                town_context += f"You may mention these streets: {', '.join([s.get('name', 'Unknown Street') for s in streets])}. "
                
        # Add landmarks if available
        if 'town_features' in article_town_data and 'landmarks' in article_town_data['town_features']:
            landmarks = article_town_data['town_features']['landmarks']
            if landmarks:
                town_context += f"You may mention these landmarks: {', '.join([l.get('name', 'Unknown Landmark') for l in landmarks])}. "
                
        # Add businesses if available
        if 'town_features' in article_town_data and 'businesses' in article_town_data['town_features']:
            businesses = article_town_data['town_features']['businesses']
            if businesses:
                town_context += f"You may mention these local businesses: {', '.join([b.get('name', 'Unknown Business') for b in businesses])}. "
    
    # Build people context string
    people_context = ""
    if article_people_data and len(article_people_data) > 0:
        people_context += "Include quotes from these people in your article:\n"
        for person in article_people_data:
            name = f"{person.get('first_name', '')} {person.get('last_name', '')}"
            people_context += f"- {name}, {person.get('age', 'Unknown')}, {person.get('occupation', 'resident')}"
            if person.get('temperament_type'):
                people_context += f", who tends to be {person.get('temperament_description', 'a local resident')}"
            people_context += ".\n"
    
    # Create user prompt using template from config
    user_prompt_template = prompt_templates.get('user_prompt', '')
    user_prompt = user_prompt_template.format(
        category=category,
        town_context=town_context,
        people_context=people_context
    )
    
    # Create messages for the API call
    messages = [
        {'role': 'user', 'content': user_prompt}
    ]
    
    # Set model parameters for article generation
    model_args = {
        'model': 'gpt-4o-mini',  # Use the appropriate model
        'temperature': 0.8,  # Slightly higher temperature for creativity
        'max_tokens': 2000,  # Allow enough tokens for a full article
        'response_format': {'type': 'json_object'}  # Request JSON response
    }
    
    try:
        # Call the OpenAI API
        response_text = call_openai_api(system_prompt, messages, model_args)
        
        # Parse the JSON response
        import json
        response_data = json.loads(response_text)
        
        # Extract the article content
        title = response_data.get('title', f"Article about {category}")
        body = response_data.get('body', "No content generated.")
        summary = response_data.get('summary', "No summary available.")
        # Extract image suggestions (defaulting to empty list if not provided)
        images = response_data.get('images', [])
        # Extract story status (defaulting to "ongoing" if not provided)
        story_status = response_data.get('story_status', "ongoing")
        # Normalize story status to ensure it's either "ongoing" or "concluded"
        story_status = story_status.lower().strip()
        if story_status not in ["ongoing", "concluded"]:
            story_status = "ongoing"  # Default if invalid value
        
        print(f"\nGenerated title: {title}")
        print(f"\nSummary: {summary[:100]}...")
        print(f"\nStory status: {story_status}")
        if images:
            print(f"\nSuggested {len(images)} images for the article")
        
        return {
            'title': title,
            'body': body,
            'summary': summary,
            'story_status': story_status,
            'images': images
        }
    except Exception as e:
        print(f"\nError generating article content: {e}")
        return {
            'title': f"Placeholder Title for {category} Article",
            'body': "This is a placeholder for the article body.",
            'summary': "This is a placeholder summary.",
            'story_status': 'ongoing',  # Default story status in case of error
            'images': []  # Empty array for images in case of error
        }

def create_new_story():
    """
    Create a new news story by sampling category and author from configuration.
    The story will be saved to articles.csv.
    
    Returns:
        Dict containing the generated article data
    """
    # Get the directory of the current file
    current_dir = Path(__file__).parent
    data_dir = Path(current_dir).parent.parent.parent / 'data'
    
    # Load configuration
    config_file = current_dir / 'article_config.yaml'
    config = load_config(config_file)
    
    # Load town and people data
    town_data_file = data_dir / 'town_data.json'
    people_data_file = data_dir / 'people_data.csv'
    
    town_data = load_town_data(town_data_file)
    people_data = load_people_data(people_data_file)
    
    # Sample category
    category = random.choice(config['categories'])
    
    # Find authors who specialize in this category if possible
    category_authors = [
        author for author in config['authors'] 
        if category in author.get('specialties', [])
    ]
    
    # If no author specializes in this category, choose any author
    if not category_authors:
        author_info = random.choice(config['authors'])
    else:
        # Higher chance (70%) of selecting an author specialized in this category
        if random.random() < 0.7:
            author_info = random.choice(category_authors)
        else:
            author_info = random.choice(config['authors'])
    
    # Extract author name and persona
    author_name = author_info['name']
    author_persona = author_info['persona']
    author_style = author_info['writing_style']
    
    # Generate article ID (timestamp-based for uniqueness)
    article_id = f"ART-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # Sample data from town and people based on article_seed
    article_town_data = {}
    article_people_data = []
    
    # Sample article seriousness level
    seriousness = "balanced"  # Default to balanced if not configured
    if 'article_seed' in config and 'tone' in config['article_seed'] and 'seriousness' in config['article_seed']['tone']:
        seriousness_weights = config['article_seed']['tone']['seriousness']
        seriousness_levels = list(seriousness_weights.keys())
        seriousness_probs = list(seriousness_weights.values())
        seriousness = random.choices(seriousness_levels, weights=seriousness_probs, k=1)[0]
    
    print(f"\n--- GENERATING ARTICLE {article_id} ---")
    print(f"Category: {category}")
    print(f"Author: {author_name} ({author_info['writing_style']})")
    print(f"Tone: {seriousness.replace('_', ' ').title()}")
    
    # Sample town data if available and according to article_seed
    if town_data and 'article_seed' in config and 'town_data' in config['article_seed']:
        town_config = config['article_seed']['town_data']
        
        # Check if we should include town data based on inclusion probability
        if random.random() < town_config.get('inclusion_probability', 0.5):
            print(f"\n=== TOWN DATA SAMPLING ===")
            print(f"Town: {town_data.get('name', 'Unknown')}")
            print(f"Population: {town_data.get('population', 0)}")
            print(f"Founded: {town_data.get('founded_year', 'Unknown')}")
            print(f"Climate: {town_data.get('climate', 'Unknown')}")
            
            # Extract relevant town features based on feature weights
            feature_weights = town_config.get('feature_weights', {})
            article_town_data = {
                'town_name': town_data.get('name', ''),
                'town_population': town_data.get('population', 0),
                'town_features': {}
            }
            
            # Sample streets
            sampled_streets = []
            if 'streets' in town_data and 'streets' in feature_weights:
                street_config = feature_weights['streets']
                if random.random() < street_config.get('probability', 0.5):
                    max_streets = street_config.get('max_count', 3)
                    num_streets = min(max_streets, len(town_data['streets']))
                    if num_streets > 0:
                        sampled_streets = random.sample(town_data['streets'], num_streets)
                        article_town_data['town_features']['streets'] = sampled_streets
                        
                        print(f"\nSampled Streets (max: {max_streets}):")
                        for street in sampled_streets:
                            print(f"  - {street.get('name', 'Unknown Street')} ({street.get('type', 'Unknown Type')})")
            
            # Sample landmarks if present
            sampled_landmarks = []
            if 'landmarks' in town_data and 'landmarks' in feature_weights:
                landmark_config = feature_weights['landmarks']
                if random.random() < landmark_config.get('probability', 0.5):
                    max_landmarks = landmark_config.get('max_count', 2)
                    num_landmarks = min(max_landmarks, len(town_data.get('landmarks', [])))
                    if num_landmarks > 0:
                        sampled_landmarks = random.sample(town_data['landmarks'], num_landmarks)
                        article_town_data['town_features']['landmarks'] = sampled_landmarks
                        
                        print(f"\nSampled Landmarks (max: {max_landmarks}):")
                        for landmark in sampled_landmarks:
                            print(f"  - {landmark.get('name', 'Unknown Landmark')} ({landmark.get('type', 'Unknown Type')})")
                            print(f"    Located on: {landmark.get('street', 'Unknown Street')}")
                            print(f"    Established: {landmark.get('established_year', 'Unknown')}")
            
            # Sample businesses if present
            sampled_businesses = []
            if 'businesses' in town_data and 'businesses' in feature_weights:
                business_config = feature_weights['businesses']
                if random.random() < business_config.get('probability', 0.5):
                    max_businesses = business_config.get('max_count', 2)
                    num_businesses = min(max_businesses, len(town_data.get('businesses', [])))
                    if num_businesses > 0:
                        sampled_businesses = random.sample(town_data['businesses'], num_businesses)
                        article_town_data['town_features']['businesses'] = sampled_businesses
                        
                        print(f"\nSampled Businesses (max: {max_businesses}):")
                        for business in sampled_businesses:
                            print(f"  - {business.get('name', 'Unknown Business')} ({business.get('type', 'Unknown Type')})")
                            print(f"    Located on: {business.get('street', 'Unknown Street')}")
                            print(f"    Founded: {business.get('founded_year', 'Unknown')}")
            
            # Sample events if present
            sampled_events = []
            if 'events' in town_data and 'events' in feature_weights:
                event_config = feature_weights['events']
                if random.random() < event_config.get('probability', 0.5):
                    max_events = event_config.get('max_count', 2)
                    num_events = min(max_events, len(town_data.get('events', [])))
                    if num_events > 0:
                        sampled_events = random.sample(town_data['events'], num_events)
                        article_town_data['town_features']['events'] = sampled_events
                        
                        print(f"\nSampled Events (max: {max_events}):")
                        for event in sampled_events:
                            print(f"  - {event.get('name', 'Unknown Event')} ({event.get('type', 'Unknown Type')})")
                            print(f"    Date: {event.get('date', 'Unknown Date')}")
                            print(f"    Location: {event.get('location', 'Unknown Location')}")
    
    # Sample people data if available and according to article_seed
    if not people_data.empty and 'article_seed' in config and 'people_data' in config['article_seed']:
        people_config = config['article_seed']['people_data']
        
        # Check if we should include people data based on inclusion probability
        if random.random() < people_config.get('inclusion_probability', 0.5):
            print(f"\n=== PEOPLE DATA SAMPLING ===")
            
            # Determine how many people to include
            min_people = people_config.get('min_people_per_article', 1)
            max_people = people_config.get('max_people_per_article', 3)
            num_people = random.randint(min_people, max_people)
            print(f"Target number of people to include: {num_people}")
            
            # Sample people
            if len(people_data) > 0:
                # Apply demographic filters if specified
                filtered_people = people_data
                chosen_age_group = "All ages"
                
                # Filter by age groups if specified
                if 'demographic_weights' in people_config and 'age' in people_config['demographic_weights']:
                    age_weights = people_config['demographic_weights']['age']
                    
                    # Choose an age group based on weights
                    age_groups = list(age_weights.keys())
                    age_probs = list(age_weights.values())
                    chosen_age_group = random.choices(age_groups, weights=age_probs, k=1)[0]
                    print(f"Selected age group: {chosen_age_group}")
                    
                    # Apply age filter
                    if chosen_age_group == "18-30":
                        filtered_people = people_data[(people_data['age'] >= 18) & (people_data['age'] <= 30)]
                    elif chosen_age_group == "31-50":
                        filtered_people = people_data[(people_data['age'] >= 31) & (people_data['age'] <= 50)]
                    elif chosen_age_group == "51-70":
                        filtered_people = people_data[(people_data['age'] >= 51) & (people_data['age'] <= 70)]
                    elif chosen_age_group == "71+":
                        filtered_people = people_data[people_data['age'] >= 71]
                
                # Sample from filtered people
                if not filtered_people.empty:
                    sample_size = min(num_people, len(filtered_people))
                    sampled_people = filtered_people.sample(sample_size)
                    article_people_data = sampled_people.to_dict('records')
                    
                    print(f"\nSampled {len(article_people_data)} people:")
                    for i, person in enumerate(article_people_data):
                        print(f"\nPerson {i+1}:")
                        print(f"  Name: {person.get('first_name', '')} {person.get('last_name', '')}")
                        print(f"  Age: {person.get('age', 'Unknown')}")
                        print(f"  Occupation: {person.get('occupation', 'Unknown')}")
                        print(f"  Location: {person.get('location', 'Unknown')}")
                        print(f"  Temperament: {person.get('temperament_type', 'Unknown')} - {person.get('temperament_description', 'Unknown')}")
                else:
                    print("No people matched the demographic filters.")
    
    # Generate article content using OpenAI
    content = generate_article_content(category, author_info, article_town_data, article_people_data, seriousness, config)
    
    # Get the generated image suggestions
    images = content.get('images', [])
    # Ensure images is a list before proceeding
    if images is None:
        images = []
    
    # Search for actual images based on the suggestions
    if images and len(images) > 0:
        print("\n=== SEARCHING FOR ARTICLE IMAGES ===")
        images_with_urls = search_for_article_images(images)
    else:
        images_with_urls = []
    
    # Convert the enhanced image list to a JSON string for storage
    images_json = json.dumps(images_with_urls)
    
    article = {
        'article_id': article_id,
        'title': content['title'],
        'slug': content['title'].lower().replace(' ', '-').replace(',', '').replace('.', '').replace('\'', '').replace('"', '')[:50],
        'body': content['body'],
        'summary': content['summary'],
        'images': images_json,  # Add the images as a JSON string
        'publication_date': datetime.datetime.now().strftime('%Y-%m-%d'),
        'last_updated': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'author': author_name,
        'author_persona': author_persona,
        'author_style': author_style,
        'category': category,
        'status': 'Draft',
        'story_status': content.get('story_status', 'Ongoing'),  # Use the LLM-provided story status
        'seriousness': seriousness,
        'parent_article_id': None,  # No parent article for new articles
    }
    
    # Define the path to the CSV file in the data directory
    csv_file = Path(current_dir).parent.parent.parent / 'data' / 'articles.csv'
    
    # Check if the file exists
    file_exists = csv_file.is_file()
    
    # Define expected columns for the DataFrame
    expected_columns = [
        'article_id', 'title', 'slug', 'body', 'summary', 'images',
        'publication_date', 'last_updated', 'author', 
        'author_persona', 'author_style', 'category', 
        'status', 'story_status', 'town_data', 'people_data',
        'seriousness', 'parent_article_id'
    ]
    
    # Convert the article dictionary to a DataFrame
    article_df = pd.DataFrame([article])
    
    if file_exists:
        try:
            # Try to read the existing CSV file
            existing_df = pd.read_csv(csv_file)
            
            # Check if the columns match
            if set(existing_df.columns) != set(expected_columns):
                print("CSV structure has changed. Creating backup and new file...")
                
                # Create a backup
                backup_file = f"{csv_file}.bak"
                import shutil
                shutil.copy2(csv_file, backup_file)
                
                # Ensure all columns are present in both DataFrames
                for col in expected_columns:
                    if col not in existing_df.columns:
                        existing_df[col] = ""
                
                # Reorder and filter columns to match expected structure
                existing_df = existing_df[expected_columns]
                
                # Concatenate with the new article and save
                updated_df = pd.concat([existing_df, article_df], ignore_index=True)
                updated_df.to_csv(csv_file, index=False)
            else:
                # Append the new article
                article_df.to_csv(csv_file, mode='a', header=False, index=False)
                
        except pd.errors.EmptyDataError:
            # File exists but is empty
            article_df.to_csv(csv_file, index=False)
            
        except Exception as e:
            # Handle other errors (like permission issues)
            print(f"Error processing CSV file: {e}")
            # Try writing new file
            article_df.to_csv(csv_file, index=False)
    else:
        # File doesn't exist, create it
        article_df.to_csv(csv_file, index=False)
    
    print(f"Created new article with ID: {article_id}")
    return article

def search_for_image(query: str, credentials_path: Optional[str] = None) -> Dict[str, str]:
    """
    Search for an image using the Unsplash API based on a query.
    
    Args:
        query: The search query string
        credentials_path: Optional path to credentials file containing API keys
        
    Returns:
        Dict containing the image URL, alt text, credit info, etc.
    """
    # First try to get API key from environment or credentials file
    api_key = os.environ.get('UNSPLASH_ACCESS_KEY')
    
    # If not found in environment, try to load from credentials file
    if not api_key and credentials_path:
        try:
            with open(credentials_path, 'r') as file:
                creds = json.load(file)
                api_key = creds.get('UNSPLASH_ACCESS_KEY')
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading credentials: {e}")
    
    # If still no API key, try default location
    if not api_key:
        default_creds_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'credentials')
        print(f"Looking for credentials file at: {default_creds_path}")
        try:
            with open(default_creds_path, 'r') as file:
                creds = json.load(file)
                api_key = creds.get('UNSPLASH_ACCESS_KEY')
                if api_key:
                    print("Found Unsplash API key in credentials file")
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading default credentials: {e}")
    
    # If no API key is available, fall back to a placeholder
    if not api_key:
        print("No Unsplash API key found. Using placeholder image.")
        return {
            "url": f"https://via.placeholder.com/800x600?text={query.replace(' ', '+')}",
            "alt_text": query,
            "credit": "Placeholder Image",
            "source": "placeholder.com",
            "search_query": query
        }
    
    # Make request to Unsplash API
    try:
        # Prepare the API request
        url = "https://api.unsplash.com/search/photos"
        params = {
            "query": query,
            "per_page": 1,  # We just need one image
            "orientation": "landscape",  # Better for articles
        }
        headers = {
            "Authorization": f"Client-ID {api_key}"
        }
        
        # Send the request
        response = httpx.get(url, params=params, headers=headers, timeout=10.0)
        response.raise_for_status()  # Raise exception for error responses
        
        # Parse the results
        data = response.json()
        results = data.get('results', [])
        
        if results:
            image = results[0]
            return {
                "url": image["urls"]["regular"],
                "thumb_url": image["urls"]["thumb"],
                "alt_text": image.get("alt_description", query) or query,
                "credit": f"Photo by {image['user']['name']} on Unsplash",
                "credit_link": image['user']['links']['html'],
                "source": "Unsplash",
                "search_query": query
            }
        else:
            print(f"No image results found for query: {query}")
            return {
                "url": f"https://via.placeholder.com/800x600?text={query.replace(' ', '+')}",
                "alt_text": query,
                "credit": "Placeholder Image",
                "source": "placeholder.com",
                "search_query": query
            }
            
    except Exception as e:
        print(f"Error searching for image: {e}")
        # Return a placeholder image as fallback
        return {
            "url": f"https://via.placeholder.com/800x600?text={query.replace(' ', '+')}",
            "alt_text": query,
            "credit": "Placeholder Image",
            "source": "placeholder.com",
            "search_query": query
        }

def search_for_article_images(article_images: List[Dict[str, str]], credentials_path: Optional[str] = None) -> List[Dict[str, str]]:
    """
    Search for all images needed for an article.
    
    Args:
        article_images: List of image objects with 'image' (query) and 'caption' fields
        credentials_path: Optional path to credentials file containing API keys
        
    Returns:
        List of image objects with URLs and metadata added
    """
    enhanced_images = []
    
    for i, img in enumerate(article_images):
        print(f"\nSearching for image {i+1}/{len(article_images)}: {img['image']}")
        
        # Rate limiting to avoid API throttling
        if i > 0:
            time.sleep(1)  # Wait 1 second between requests
            
        # Get image info from search
        image_info = search_for_image(img['image'], credentials_path)
        
        # Create enhanced image object with original data plus search results
        enhanced_image = {
            **img,  # Include original image and caption
            **image_info  # Add the URL and other metadata
        }
        
        enhanced_images.append(enhanced_image)
        
    return enhanced_images

if __name__ == "__main__":
    create_new_story()
