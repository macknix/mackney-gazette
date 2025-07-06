"""
Single Town Generator Module

This module generates realistic single town infrastructure data for 
simulation and data analysis purposes. It creates comprehensive town
data including streets, landmarks, businesses, parks, schools, and other
municipal infrastructure elements seeded by country-specific characteristics.

Key Features:
- Single town generation (no bulk generation)
- Multi-locale support for country-specific town generation
- Realistic infrastructure distributions based on town size
- Weighted random generation for authentic civic patterns
- YAML-based configuration for easy customization
- Configurable random seeds for reproducible results
- Integration with Faker for realistic data generation

Example Usage:
    # Generate data for a specific locale
    generator = TownGenerator(locale="en_GB", seed=42)
    
    # Generate single town infrastructure
    town = generator.generate_town("Riverside", size="medium")
    
    # Save to JSON file
    generator.save_to_json("my_town.json")

Classes:
    TownGenerator: Main class for single town infrastructure data generation
"""

import random
import os
import yaml
from datetime import datetime
from typing import Dict, Optional
import uuid
from faker import Faker

import json
from typing import List


class TownGenerator:
    """
    Generates realistic single town infrastructure data.
    """
    
    def __init__(self, locale: str = "en_US", seed: Optional[int] = None):
        """
        Initialize the town generator.
        
        Args:
            locale (str): Faker locale to use for data generation. Defaults to "en_US".
                         Examples: "en_US", "en_GB", "fr_FR", "de_DE", "es_ES", "it_IT", etc.
            seed (int, optional): Random seed for reproducible results.
        """
        if seed is not None:
            random.seed(seed)
            Faker.seed(seed)
        
        # Initialize Faker with specified locale
        self.fake = Faker(locale)
        self.locale = locale
        
        # Load configuration from YAML file
        config_path = os.path.join(os.path.dirname(__file__), 'town_config.yaml')
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        # Extract configuration sections for easy access
        self.town_sizes = self.config['town_sizes']
        self.street_patterns = self.config['street_patterns']
        self.business_types = self.config['business_types']
        self.landmark_types = self.config['landmark_types']
        self.park_types = self.config['park_types']
        self.school_types = self.config['school_types']
        self.service_types = self.config['service_types']
        self.country_mapping = self.config['country_mapping']
        self.name_components = self.config['name_components']
    
    def get_country_name(self) -> str:
        """Get the country name for the current locale."""
        return self.country_mapping.get(self.locale, "Unknown")
    
    @staticmethod
    def get_available_locales() -> List[str]:
        """Get list of available locales."""
        config_path = os.path.join(os.path.dirname(__file__), 'town_config.yaml')
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        return list(config['country_mapping'].keys())
    
    def _generate_street_name(self) -> str:
        """Generate a realistic street name based on locale."""
        patterns = self.street_patterns.get(self.locale, self.street_patterns[self.locale])
        
        # Generate street name using various patterns
        patterns_methods = [
            lambda: f"{self.fake.last_name()} {random.choice(patterns)}",
            lambda: f"{self.fake.first_name()} {random.choice(patterns)}",
            lambda: f"{random.choice(self.name_components['tree_names'])} {random.choice(patterns)}",
            lambda: f"{random.choice(self.name_components['street_prefixes'])} {random.choice(patterns)}",
            lambda: f"{random.choice(self.name_components['directional_prefixes'])} {random.choice(patterns)}",
            lambda: f"{random.choice(self.name_components['ordinal_prefixes'])} {random.choice(patterns)}"
        ]
        
        return random.choice(patterns_methods)()
    
    def _generate_business_name(self, business_type: str) -> str:
        """Generate a realistic business name based on type."""
        adjectives = self.name_components['business_name_adjectives']
        
        if business_type == "Restaurant/Café":
            patterns = [
                f"{self.fake.last_name()}'s Restaurant",
                f"The {random.choice(adjectives['descriptive'])} {random.choice(self.name_components['business_name_nouns']['restaurant'])}",
                f"{random.choice(['Mama', 'Papa', 'Tony', 'Mario', 'Luigi'])}'s {random.choice(['Pizza', 'Diner', 'Bistro', 'Café'])}",
                f"{self.fake.city()[:6]} {random.choice(['Grill', 'Diner', 'Café', 'Bistro'])}"
            ]
        elif business_type == "Retail Store":
            patterns = [
                f"{self.fake.last_name()}'s {random.choice(self.name_components['business_name_nouns']['retail'])}",
                f"{random.choice(adjectives['location_based'])} {random.choice(['Market', 'Store', 'Shop'])}",
                f"The {random.choice(adjectives['size_based'])} {random.choice(['Shop', 'Store', 'Market'])}"
            ]
        elif business_type == "Gas Station":
            patterns = [
                f"{random.choice(adjectives['speed_based'])} {random.choice(self.name_components['business_name_nouns']['gas'])}",
                f"{self.fake.last_name()}'s {random.choice(['Gas', 'Fuel', 'Service'])}",
                f"{random.choice(adjectives['location_based'])} {random.choice(['Gas', 'Fuel', 'Station'])}"
            ]
        else:
            # Generic business names
            patterns = [
                f"{self.fake.last_name()}'s {business_type.split('/')[0]}",
                f"{self.fake.city()[:6]} {business_type.split('/')[0]}",
                f"{random.choice(adjectives['descriptive'])} {business_type.split('/')[0]}"
            ]
        
        return random.choice(patterns)
    
    def _generate_landmark_name(self, landmark_type: str) -> str:
        """Generate a realistic landmark name."""
        if "Church" in landmark_type:
            return f"St. {self.fake.first_name()}'s Church"
        elif landmark_type == "Monument":
            return f"{self.fake.last_name()} {random.choice(['Monument', 'Memorial'])}"
        elif landmark_type == "Statue":
            return f"{self.fake.name()} Statue"
        elif landmark_type == "Historic Building":
            return f"Old {random.choice(['Town Hall', 'Opera House', 'Bank Building', 'Hotel', 'Mill'])}"
        elif landmark_type == "Museum":
            return f"{self.fake.city()[:8]} {random.choice(['History', 'Art', 'Natural History'])} Museum"
        else:
            return f"{self.fake.city()[:8]} {landmark_type}"
    
    def _generate_park_name(self, park_type: str) -> str:
        """Generate a realistic park name."""
        name_patterns = [
            f"{self.fake.last_name()} {park_type}",
            f"{random.choice(self.name_components['park_prefixes'])} {park_type}",
            f"{random.choice(self.name_components['tree_names'])} {park_type}",
            f"Memorial {park_type}"
        ]
        return random.choice(name_patterns)
    
    def _generate_school_name(self, school_type: str) -> str:
        """Generate a realistic school name."""
        if "Elementary" in school_type:
            return f"{self.fake.last_name()} Elementary School"
        elif "Middle" in school_type:
            return f"{self.fake.city()[:8]} Middle School"
        elif "High" in school_type:
            return f"{self.fake.city()[:8]} High School"
        else:
            return f"{self.fake.last_name()} {school_type}"
    
    def generate_town(self, town_name: Optional[str] = None, size: str = "medium") -> Dict:
        """
        Generate a complete town with all infrastructure elements.
        
        Args:
            town_name (str, optional): Name of the town. If None, generates random name.
            size (str): Size category - "small", "medium", or "large".
            
        Returns:
            Dict: Complete town data structure.
        """
        if size not in self.town_sizes:
            raise ValueError(f"Invalid size '{size}'. Must be one of: {list(self.town_sizes.keys())}")
        
        size_config = self.town_sizes[size]
        
        # Generate basic town info
        if town_name is None:
            town_name = self.fake.city()
        
        population = random.randint(*size_config["population_range"])
        
        # Generate streets
        street_count = random.randint(*size_config["street_count_range"])
        streets = []
        for _ in range(street_count):
            streets.append({
                "id": str(uuid.uuid4()),
                "name": self._generate_street_name(),
                "type": random.choice(["Residential", "Commercial", "Mixed", "Industrial"]),
                "length_km": round(random.uniform(0.2, 2.5), 2)
            })
        
        # Generate businesses
        business_count = random.randint(*size_config["business_count_range"])
        businesses = []
        for _ in range(business_count):
            business_type = random.choices(
                list(self.business_types.keys()),
                weights=list(self.business_types.values())
            )[0]
            
            businesses.append({
                "id": str(uuid.uuid4()),
                "name": self._generate_business_name(business_type),
                "type": business_type,
                "street": random.choice(streets)["name"],
                "employees": random.randint(1, 50),
                "established_year": random.randint(1950, 2023)
            })
        
        # Generate landmarks
        landmark_count = random.randint(*size_config["landmark_count_range"])
        landmarks = []
        for _ in range(landmark_count):
            landmark_type = random.choice(self.landmark_types)
            landmarks.append({
                "id": str(uuid.uuid4()),
                "name": self._generate_landmark_name(landmark_type),
                "type": landmark_type,
                "street": random.choice(streets)["name"],
                "established_year": random.randint(1800, 2020),
                "historical_significance": random.choice(self.name_components["historical_significance_levels"])
            })
        
        # Generate parks
        park_count = random.randint(*size_config["park_count_range"])
        parks = []
        for _ in range(park_count):
            park_type = random.choice(self.park_types)
            parks.append({
                "id": str(uuid.uuid4()),
                "name": self._generate_park_name(park_type),
                "type": park_type,
                "area_hectares": round(random.uniform(0.5, 20.0), 2),
                "facilities": random.choices(
                    self.name_components["facility_types"],
                    k=random.randint(1, 4)
                )
            })
        
        # Generate schools
        school_count = random.randint(*size_config["school_count_range"])
        schools = []
        for _ in range(school_count):
            school_type = random.choice(self.school_types)
            schools.append({
                "id": str(uuid.uuid4()),
                "name": self._generate_school_name(school_type),
                "type": school_type,
                "street": random.choice(streets)["name"],
                "students": random.randint(50, 1200),
                "established_year": random.randint(1900, 2020)
            })
        
        # Generate public services
        service_count = random.randint(*size_config["service_count_range"])
        services = []
        for _ in range(service_count):
            service_type = random.choice(self.service_types)
            services.append({
                "id": str(uuid.uuid4()),
                "name": f"{town_name} {service_type}",
                "type": service_type,
                "street": random.choice(streets)["name"],
                "operating_hours": f"{random.randint(6, 9)}:00 AM - {random.randint(4, 8)}:00 PM",
                "staff_count": random.randint(2, 25)
            })
        
        # Store the generated town data
        self.town_data = {
            "id": str(uuid.uuid4()),
            "name": town_name,
            "country": self.get_country_name(),
            "locale": self.locale,
            "size_category": size,
            "population": population,
            "area_sq_km": round(population / random.randint(100, 500), 2),
            "founded_year": random.randint(1600, 1950),
            "elevation_m": random.randint(0, 1500),
            "climate": random.choice(self.name_components["climate_types"]),
            "streets": streets,
            "businesses": businesses,
            "landmarks": landmarks,
            "parks": parks,
            "schools": schools,
            "services": services,
            "generated_at": datetime.now().isoformat()
        }
        
        return self.town_data
    
    def save_to_json(self, filename: str = "town_data.json", output_dir: str = ".") -> str:
        """
        Save the generated town data to a JSON file.
        
        Args:
            filename (str): Name of the JSON file.
            output_dir (str): Directory to save the file.
            
        Returns:
            str: Full path to the created JSON file.
        """
        if not hasattr(self, 'town_data') or self.town_data is None:
            raise ValueError("No town data to save. Call generate_town() first.")
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, filename)
        
        # Write to JSON
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.town_data, f, indent=2, ensure_ascii=False)
        except OSError as e:
            raise OSError(f"Unable to write JSON file '{filepath}': {e}")
        
        print(f"Generated town '{self.town_data['name']}' and saved to: {filepath}")
        return filepath

def generate_town_json(town_name: Optional[str] = None, size: str = "medium", 
                      locale: str = "en_US", seed: Optional[int] = None, 
                      filename: str = "town_data.json", output_dir: str = ".") -> str:
    """
    Convenience function to generate a single town and save as JSON.
    
    Args:
        town_name (str, optional): Name of the town. If None, generates random name.
        size (str): Size category - "small", "medium", or "large".
        locale (str): Faker locale to use for data generation.
        seed (int, optional): Random seed for reproducible results.
        filename (str): Name of the JSON file.
        output_dir (str): Directory to save the file.
        
    Returns:
        str: Full path to the created JSON file.
    """
    if locale not in TownGenerator.get_available_locales():
        raise ValueError(f"Invalid locale '{locale}'. Available locales: {TownGenerator.get_available_locales()}")
    
    generator = TownGenerator(locale=locale, seed=seed)
    generator.generate_town(town_name, size)
    return generator.save_to_json(filename, output_dir)


if __name__ == "__main__":
    # Show available locales
    print("Available locales:")
    available_locales = TownGenerator.get_available_locales()
    for locale in available_locales:
        config_path = os.path.join(os.path.dirname(__file__), 'town_config.yaml')
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        print(f"  {locale}: {config['country_mapping'].get(locale, 'Unknown')}")
    
    print("\n" + "="*50)
    
    # Example usage with different locales
    locale = "en_GB"
    
    try:
        print(f"\nGenerating town data for {locale}:")
        generator = TownGenerator(locale=locale, seed=42)
        
        # Generate sample town
        town = generator.generate_town("Parp", size="medium")
        print(f"Generated town: {town['name']}")
        print(f"  Country: {town['country']}")
        print(f"  Population: {town['population']:,}")
        print(f"  Streets: {len(town['streets'])}")
        print(f"  Businesses: {len(town['businesses'])}")
        print(f"  Landmarks: {len(town['landmarks'])}")
        print(f"  Parks: {len(town['parks'])}")
        print(f"  Schools: {len(town['schools'])}")
        print(f"  Services: {len(town['services'])}")
        
        # Show some sample streets
        print(f"\nSample streets:")
        for street in town['streets'][:5]:
            print(f"  - {street['name']} ({street['type']}, {street['length_km']} km)")
        
        # Show some sample businesses
        print(f"\nSample businesses:")
        for business in town['businesses'][:5]:
            print(f"  - {business['name']} ({business['type']}) on {business['street']}")
        
        # Save town data as JSON
        json_filename = generator.save_to_json("town_data.json", "data")
        print(f"\nDetailed town data saved to: {json_filename}")
        print(f"This file contains complete infrastructure details for {town['name']}")
        print(f"including all {len(town['streets'])} streets, {len(town['businesses'])} businesses,")
        print(f"{len(town['landmarks'])} landmarks, and more.")
        
    except Exception as e:
        print(f"Error generating town data for {locale}: {e}")