"""
Town Initialization Module

This module reads town initialization parameters from a configuration file
and initializes the town and population data using the town and people generators.

Usage:
    python -m src.initialise_town [--config CONFIG_PATH]

Parameters:
    --config: Optional path to configuration file (defaults to town_init_config.yaml in project root)
"""

import os
import yaml
import argparse
from typing import Optional

from src.utils.data.generate_town import TownGenerator
from src.utils.data.generate_people import generate_demographic_csv


def initialise_town(config_path: Optional[str] = None):
    """
    Initialize town and population based on configuration file.
    
    Args:
        config_path: Path to the configuration file. If None, uses default.
    """
    # Use default config path if none provided
    if config_path is None:
        # Look for config in project root directory
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(project_root, "town_init_config.yaml")
    
    # Load configuration
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    
    # Extract town configuration
    town_name = config["town"]["name"]
    locale = config["town"]["locale"]
    seed = config["town"]["seed"]
    
    # Calculate population size
    population_scale = config["population"]["scale_factor"]
    min_people = config["population"]["min_people"]
    
    # Print initialization information
    print(f"Initializing town: {town_name}")
    print(f"Locale: {locale}")
    print(f"Seed: {seed}")
    
    # Create the town generator and generate a town
    town_generator = TownGenerator(locale=locale, seed=seed)
    
    # Generate town data with the specified name
    town_data = town_generator.generate_town(town_name=town_name)
    
    # Add newspaper information if available in config
    if "newspaper" in config:
        town_data["newspaper"] = {
            "name": config["newspaper"]["name"],
            "tagline": config["newspaper"]["tagline"],
            "founded_year": config["newspaper"]["founded_year"],
            "publication_frequency": config["newspaper"]["publication_frequency"]
        }
        
    # Log detailed town information
    print("\n===== TOWN DETAILS =====")
    print(f"Town Name: {town_data['name']}")
    print(f"Population: {town_data['population']:,}")
    print(f"Founded: {town_data.get('founded_year', 'Unknown')}")
    if 'area_km2' in town_data:
        print(f"Area: {town_data['area_km2']:.2f} km²")
    print(f"Country: {town_data.get('country', 'United Kingdom')}")
    
    # Log infrastructure counts
    print("\n----- Infrastructure -----")
    print(f"Streets: {len(town_data.get('streets', []))}")
    print(f"Businesses: {len(town_data.get('businesses', []))}")
    print(f"Landmarks: {len(town_data.get('landmarks', []))}")
    print(f"Parks: {len(town_data.get('parks', []))}")
    print(f"Schools: {len(town_data.get('schools', []))}")
    print(f"Municipal Services: {len(town_data.get('services', []))}")
    
    # Log some sample businesses
    if town_data.get('businesses'):
        print("\n----- Notable Establishments -----")
        # Sort businesses by importance if available, otherwise show first 5
        businesses = town_data['businesses']
        if businesses and 'importance' in businesses[0]:
            sorted_businesses = sorted(businesses, key=lambda x: x.get('importance', 0), reverse=True)[:5]
        else:
            sorted_businesses = businesses[:5]
            
        for i, business in enumerate(sorted_businesses):
            print(f"{i+1}. {business['name']} ({business['type']}) - {business.get('street', 'Unknown location')}")
    
    # Log newspaper information
    if "newspaper" in town_data:
        print(f"\n----- Local Newspaper -----")
        print(f"Name: {town_data['newspaper']['name']}")
        print(f"Tagline: {town_data['newspaper']['tagline']}")
        print(f"Founded: {town_data['newspaper']['founded_year']}")
        print(f"Frequency: {town_data['newspaper']['publication_frequency']}")
    
    print("\n=========================")
    
    # Save town data to JSON
    json_path = town_generator.save_to_json("town_data.json", "data")
    print(f"Town data saved to {json_path}")
    
    # Determine population size
    town_population = town_data.get("population", 1000)
    num_people = max(min_people, int(town_population * population_scale))
    print(f"Generating population: {num_people} people")
    
    # Generate and save demographic data to CSV
    csv_path = generate_demographic_csv(num_people, "people_data.csv", 
                                      output_dir="data", locale=locale, seed=seed)
    print(f"Population data saved to {csv_path}")
    
    # Display population statistics
    print("\n===== POPULATION DETAILS =====")
    print(f"Total town population: {town_population:,}")
    print(f"Generated residents: {num_people:,} ({population_scale*100:.1f}% of total)")
    print(f"Data stored in: {csv_path}")
    
    print("\nTown initialization completed successfully!")


def main():
    """
    Main function to run the town initialization.
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Initialize town and population data")
    parser.add_argument("--config", help="Path to configuration file", default=None)
    args = parser.parse_args()
    
    # Initialize town
    initialise_town(args.config)


if __name__ == "__main__":
    main()
