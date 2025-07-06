"""
People data generator module using Faker library.

This module provides comprehensive demographic data generation capabilities
for testing, simulation, and data analysis purposes. It generates realistic
census-like data including personal information, employment details, 
education levels, income distribution, and psychological temperament profiles.

Key Features:
- Multi-locale support for international data generation
- Realistic demographic distributions based on age cohorts
- Weighted random generation for authentic data patterns
- Comprehensive temperament modeling with psychological traits
- CSV export functionality with proper error handling
- Configurable random seeds for reproducible results

Example Usage:
    # Generate data for a specific locale
    generator = PeopleGenerator(locale="en_GB", seed=42)
    
    # Generate single person
    person = generator.generate_person()
    
    # Generate dataset
    dataset = generator.generate_dataset(1000)
    
    # Save to CSV
    generator.save_to_csv(1000, "demographics.csv", "output")
    
    # Quick generation
    generate_demographic_csv(500, "test_data.csv", locale="fr_FR")

Classes:
    PeopleGenerator: Main class for demographic data generation
    
Functions:
    generate_demographic_csv: Convenience function for quick CSV generation
"""

import random
import csv
import os
import json
import yaml
from datetime import datetime
from typing import List, Dict, Optional, Any
import uuid
from faker import Faker


class PeopleGenerator:
    """
    Generates realistic demographic data using the Faker library.
    Configuration is loaded from people_config.yaml.
    """
    
    def __init__(self, locale: str = "en_US", seed: Optional[int] = None):
        """
        Initialize the people generator.
        
        Args:
            locale (str): Faker locale to use for data generation. Defaults to "en_US".
                         Examples: "en_US", "en_GB", "fr_FR", "de_DE", "es_ES", "it_IT", etc.
            seed (int, optional): Random seed for reproducible results.
        """
        # Load configuration from YAML file
        self.config = self._load_config()
        
        if seed is not None:
            random.seed(seed)
            Faker.seed(seed)
        
        # Initialize Faker with specified locale
        self.fake = Faker(locale)
        self.locale = locale
        
        # Load street names from town_data.json if available
        self.street_names = self._load_street_names()
        
        # Get constants from config
        age_ranges = self.config.get('age_ranges', {})
        self.MIN_AGE = age_ranges.get('min_age', 18)
        self.MAX_AGE = age_ranges.get('max_age', 99)
        self.WORKING_AGE_START = age_ranges.get('working_age_start', 25)
        self.WORKING_AGE_END = age_ranges.get('working_age_end', 65)
        self.RETIREMENT_AGE = age_ranges.get('retirement_age', 65)
        
        income_ranges = self.config.get('income_ranges', {})
        self.MIN_INCOME = income_ranges.get('min_income', 0)
        self.UNEMPLOYED_MAX_INCOME = income_ranges.get('unemployed_max_income', 15000)
        self.RETIRED_MIN_INCOME = income_ranges.get('retired_min_income', 20000)
        self.RETIRED_MAX_INCOME = income_ranges.get('retired_max_income', 60000)
        self.PART_TIME_MIN_INCOME = income_ranges.get('part_time_min_income', 15000)
        self.PART_TIME_MAX_INCOME = income_ranges.get('part_time_max_income', 40000)
        
        income_age_multipliers = self.config.get('income_age_multipliers', {})
        self.PEAK_EARNING_AGE_START = income_age_multipliers.get('peak_earning_age_start', 30)
        self.PEAK_EARNING_AGE_END = income_age_multipliers.get('peak_earning_age_end', 55)
        self.PEAK_EARNING_MULTIPLIER = income_age_multipliers.get('peak_earning_multiplier', 1.2)
        self.NORMAL_EARNING_MULTIPLIER = income_age_multipliers.get('normal_earning_multiplier', 1.0)
        self.REDUCED_EARNING_MULTIPLIER = income_age_multipliers.get('reduced_earning_multiplier', 0.8)
        
        # Load lists from config
        self.education_levels = self.config.get('education_levels', [
            "Less than high school",
            "High school diploma/GED"]) 
        
        # Employment status (universal across locales)
        self.employment_status = self.config.get('employment_status', [
            "Employed full-time",
            "Employed part-time",
            "Unemployed",
            "Retired",
            "Student",
            "Homemaker",
            "Disabled",
            "Self-employed"
        ])
        
        # Marital status (universal across locales)
        self.marital_status = self.config.get('marital_status', [
            "Single",
            "Married",
            "Divorced",
            "Widowed",
            "Separated",
            "Domestic partnership"
        ])
        
        # Temperament types with descriptions
        self.temperaments = self.config.get('temperaments', [
            {
                "type": "Optimistic",
                "description": "Generally positive outlook, sees the good in situations",
                "traits": ["positive", "hopeful", "cheerful"]
            }
        ])
        
        # Locale-specific country name mapping
        self.country_mapping = self.config.get('country_mapping', {
            "en_US": "United States",
            "en_GB": "United Kingdom",
            "en_CA": "Canada",
            "fr_FR": "France",
            "de_DE": "Germany",
            "es_ES": "Spain",
            "it_IT": "Italy",
            "pt_BR": "Brazil",
            "ja_JP": "Japan",
            "ko_KR": "South Korea",
            "zh_CN": "China",
            "ru_RU": "Russia",
            "ar_SA": "Saudi Arabia",
            "hi_IN": "India",
            "nl_NL": "Netherlands",
            "sv_SE": "Sweden",
            "no_NO": "Norway",
            "da_DK": "Denmark",
            "fi_FI": "Finland",
            "pl_PL": "Poland"
        })
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration from people_config.yaml file.
        
        Returns:
            Dict[str, Any]: Configuration dictionary.
        """
        try:
            # First try to load from the current directory
            config_path = os.path.join(os.path.dirname(__file__), 'people_config.yaml')
            
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except (FileNotFoundError, yaml.YAMLError) as e:
            print(f"Warning: Could not load people_config.yaml: {e}")
            return {}
    
    @classmethod
    def get_available_locales(cls) -> List[str]:
        """
        Get list of commonly used Faker locales.
        
        Returns:
            List[str]: List of available locale codes.
        """
        try:
            # Try to load from config file
            config_path = os.path.join(os.path.dirname(__file__), 'people_config.yaml')
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                if 'available_locales' in config:
                    return config['available_locales']
        except (FileNotFoundError, yaml.YAMLError):
            # Fall back to hardcoded values
            pass
            
        return [
            "en_US",  # United States
            "en_GB",  # United Kingdom
            "en_CA",  # Canada
            "fr_FR",  # France
            "de_DE",  # Germany
            "es_ES",  # Spain
            "it_IT",  # Italy
            "pt_BR",  # Brazil
            "ja_JP",  # Japan
            "ko_KR",  # South Korea
            "zh_CN",  # China
            "ru_RU",  # Russia
            "ar_SA",  # Saudi Arabia
            "hi_IN",  # India
            "nl_NL",  # Netherlands
            "sv_SE",  # Sweden
            "no_NO",  # Norway
            "da_DK",  # Denmark
            "fi_FI",  # Finland
            "pl_PL"   # Poland
        ]
    
    def get_country_name(self) -> str:
        """Get the country name for the current locale."""
        return self.country_mapping.get(self.locale, self.locale.split('_')[-1])
    
    def generate_person(self) -> Dict[str, str]:
        """
        Generate a single person with demographic data.
        
        Returns:
            Dict[str, str]: Dictionary containing demographic information.
        """
        # Generate basic demographics using Faker
        gender = random.choice(["Male", "Female"])
        if gender == "Male":
            first_name = self.fake.first_name_male()
        else:
            first_name = self.fake.first_name_female()
        
        last_name = self.fake.last_name()
        
        # Generate age (weighted towards working age population)
        age = self._generate_weighted_age()
        
        # Generate birth year
        current_year = datetime.now().year
        birth_year = current_year - age
        
        # Generate other demographics using Faker where possible
        education = self._generate_weighted_education(age)
        employment = self._generate_weighted_employment(age)
        occupation = self.fake.job() if "Employed" in employment else ""
        
        # Generate income based on education and employment
        income = self._generate_income(education, employment, age)
        
        # Generate household size
        household_size = self._generate_household_size(age)
        
        # Generate marital status
        marital = self._generate_weighted_marital_status(age)
        
        # Generate location using Faker
        if hasattr(self.fake, 'state'):
            location = self.fake.state()
        elif hasattr(self.fake, 'city'):
            location = self.fake.city()
        else:
            location = self.fake.address().split('\n')[0]  # First line of address
        
        # Generate full address
        address = self._generate_address_with_town_streets()
        
        # Generate phone number
        phone = self.fake.phone_number()
        
        # Generate email
        email = self.fake.email()
        
        # Generate temperament
        temperament = self._generate_temperament(age, education, employment)
        
        # Generate unique ID
        person_id = str(uuid.uuid4())[:8]
        
        return {
            "id": person_id,
            "first_name": first_name,
            "last_name": last_name,
            "age": str(age),
            "gender": gender,
            "birth_year": str(birth_year),
            "marital_status": marital,
            "education_level": education,
            "employment_status": employment,
            "occupation": occupation,
            "annual_income": str(income),
            "household_size": str(household_size),
            "location": location,
            "full_address": address,
            "phone_number": phone,
            "email": email,
            "temperament_type": temperament["type"],
            "temperament_description": temperament["description"],
            "temperament_traits": ", ".join(temperament["traits"]),
            "country": self.get_country_name(),
            "locale": self.locale
        }
    
    def _generate_weighted_age(self) -> int:
        """Generate age with realistic distribution."""
        # Weight towards working age population (25-65)
        weights = []
        ages = list(range(self.MIN_AGE, self.MAX_AGE + 1))
        
        for age in ages:
            if self.WORKING_AGE_START <= age <= self.WORKING_AGE_END:
                weights.append(3)  # Higher weight for working age
            elif self.MIN_AGE <= age <= 24 or 66 <= age <= 75:
                weights.append(2)  # Medium weight
            else:
                weights.append(1)  # Lower weight for very young/old
        
        return random.choices(ages, weights=weights)[0]
    
    def _generate_weighted_education(self, age: int) -> str:
        """Generate education level based on age."""
        if age < 25:
            # Younger people less likely to have advanced degrees
            return random.choices(
                self.education_levels[:5],  # Up to bachelor's
                weights=[15, 30, 25, 15, 15]
            )[0]
        elif age < 40:
            # Prime education completion age
            return random.choices(
                self.education_levels,
                weights=[5, 20, 15, 15, 25, 15, 3, 2]
            )[0]
        else:
            # Older generation with different education patterns
            return random.choices(
                self.education_levels,
                weights=[10, 25, 20, 15, 20, 8, 1, 1]
            )[0]
    
    def _generate_weighted_employment(self, age: int) -> str:
        """Generate employment status based on age."""
        if age < self.WORKING_AGE_START:
            return random.choices(
                self.employment_status,
                weights=[40, 30, 15, 0, 10, 3, 1, 1]
            )[0]
        elif age < self.RETIREMENT_AGE:
            return random.choices(
                self.employment_status,
                weights=[60, 15, 8, 2, 2, 5, 3, 5]
            )[0]
        else:
            return random.choices(
                self.employment_status,
                weights=[10, 10, 2, 70, 0, 3, 3, 2]
            )[0]
    
    def _generate_weighted_marital_status(self, age: int) -> str:
        """Generate marital status based on age."""
        if age < 25:
            return random.choices(
                self.marital_status,
                weights=[70, 25, 2, 1, 1, 1]
            )[0]
        elif age < 40:
            return random.choices(
                self.marital_status,
                weights=[35, 50, 8, 2, 3, 2]
            )[0]
        elif age < 65:
            return random.choices(
                self.marital_status,
                weights=[20, 60, 12, 3, 3, 2]
            )[0]
        else:
            return random.choices(
                self.marital_status,
                weights=[15, 50, 10, 20, 3, 2]
            )[0]
    
    def _generate_income(self, education: str, employment: str, age: int) -> int:
        """Generate income based on education, employment, and age."""
        # Handle special employment cases
        if "Unemployed" in employment or "Student" in employment:
            return random.randint(self.MIN_INCOME, self.UNEMPLOYED_MAX_INCOME)
        elif "Retired" in employment:
            return random.randint(self.RETIRED_MIN_INCOME, self.RETIRED_MAX_INCOME)
        elif "part-time" in employment:
            return random.randint(self.PART_TIME_MIN_INCOME, self.PART_TIME_MAX_INCOME)
        
        # Base income by education level
        education_income_map = {
            "Less than high school": 25000,
            "High school diploma/GED": 35000,
            "Some college, no degree": 40000,
            "Associate degree": 45000,
            "Bachelor's degree": 60000,
            "Master's degree": 75000,
            "Professional degree": 100000,
            "Doctoral degree": 90000
        }
        
        base_income = education_income_map.get(education, 35000)
        
        # Apply age-based income multiplier (peak earning years)
        if self.PEAK_EARNING_AGE_START <= age <= self.PEAK_EARNING_AGE_END:
            age_multiplier = self.PEAK_EARNING_MULTIPLIER
        elif self.WORKING_AGE_START <= age <= self.WORKING_AGE_END:
            age_multiplier = self.NORMAL_EARNING_MULTIPLIER
        else:
            age_multiplier = self.REDUCED_EARNING_MULTIPLIER
        
        # Add randomness to income calculation
        income = int(base_income * age_multiplier * random.uniform(0.7, 1.5))
        return max(self.MIN_INCOME, income)
    
    def _generate_household_size(self, age: int) -> int:
        """Generate household size based on age."""
        if age < 30:
            return random.choices([1, 2, 3, 4], weights=[40, 35, 20, 5])[0]
        elif age < 50:
            return random.choices([1, 2, 3, 4, 5], weights=[20, 30, 30, 15, 5])[0]
        else:
            return random.choices([1, 2, 3], weights=[30, 50, 20])[0]
    
    def _generate_temperament(self, age: int, education: str, employment: str) -> Dict[str, str]:
        """
        Generate temperament based on age, education, and employment status.
        
        Args:
            age (int): Person's age
            education (str): Education level
            employment (str): Employment status
            
        Returns:
            Dict[str, str]: Dictionary containing temperament information
        """
        temperament_weights = []
        
        for temperament in self.temperaments:
            weight = self._calculate_temperament_weight(temperament, age, education, employment)
            temperament_weights.append(max(0.1, weight))  # Ensure minimum weight
        
        # Select temperament based on weights
        selected_temperament = random.choices(self.temperaments, weights=temperament_weights)[0]
        
        return {
            "type": selected_temperament["type"],
            "description": selected_temperament["description"],
            "traits": selected_temperament["traits"]
        }
    
    def _calculate_temperament_weight(self, temperament: Dict[str, str], age: int, 
                                    education: str, employment: str) -> float:
        """Calculate weight for a temperament based on demographic factors."""
        weight = 1.0  # Base weight
        temperament_type = temperament["type"]
        
        # Age-based adjustments
        weight += self._get_age_weight_adjustment(temperament_type, age)
        
        # Education-based adjustments
        weight += self._get_education_weight_adjustment(temperament_type, education)
        
        # Employment-based adjustments
        weight += self._get_employment_weight_adjustment(temperament_type, employment)
        
        return weight
    
    def _get_age_weight_adjustment(self, temperament_type: str, age: int) -> float:
        """Get age-based weight adjustment for temperament."""
        # Get adjustments from config if available
        try:
            age_adjustments = self.config.get('temperament_weight_adjustments', {}).get('age_based', {})
            if temperament_type in age_adjustments:
                temp_adj = age_adjustments[temperament_type]
                
                # Process adjustments based on age ranges
                for age_range, value in temp_adj.items():
                    if age_range == "<30" and age < 30:
                        return value
                    elif age_range == ">60" and age > 60:
                        return value
                    elif age_range == ">50" and age > 50:
                        return value
                    elif age_range == "<25" and age < 25:
                        return value
                    elif age_range == "25-45" and 25 <= age <= 45:
                        return value
                    elif age_range == ">65" and age > 65:
                        return value
                    elif age_range == ">40" and age > 40:
                        return value
                    elif age_range == ">50" and age > 50:
                        return value
                
                # Return default if no specific range matched
                if "default" in temp_adj:
                    return temp_adj["default"]
        except (KeyError, TypeError):
            # Fall back to hardcoded values if config is not available
            pass
            
        # Fallback adjustments if not in config
        adjustments = {
            "Anxious": 0.5 if age < 30 else -0.2 if age > 60 else 0,
            "Calm": 0.3 if age > 50 else -0.1 if age < 25 else 0,
            "Outgoing": 0.3 if 25 <= age <= 45 else -0.2 if age > 65 else 0,
            "Patient": 0.4 if age > 40 else -0.2 if age < 25 else 0,
            "Impulsive": 0.4 if age < 30 else -0.3 if age > 50 else 0,
            "Ambitious": 0.4 if 25 <= age <= 45 else -0.2 if age > 60 else 0,
        }
        return adjustments.get(temperament_type, 0)
    
    def _get_education_weight_adjustment(self, temperament_type: str, education: str) -> float:
        """Get education-based weight adjustment for temperament."""
        adjustment = 0
        
        try:
            # Get education adjustments from config
            education_adjustments = self.config.get('temperament_weight_adjustments', {}).get('education_based', {})
            
            if temperament_type in education_adjustments:
                if "has_degree" in education_adjustments[temperament_type] and "degree" in education.lower():
                    adjustment += education_adjustments[temperament_type]["has_degree"]
                    
                if "advanced_degree" in education_adjustments[temperament_type] and any(level in education for level in ["Master's", "Doctoral", "Professional"]):
                    adjustment += education_adjustments[temperament_type]["advanced_degree"]
                    
                if "bachelor_or_masters" in education_adjustments[temperament_type] and any(level in education for level in ["Bachelor's", "Master's"]):
                    adjustment += education_adjustments[temperament_type]["bachelor_or_masters"]
                    
            return adjustment
            
        except (KeyError, TypeError):
            # Fall back to hardcoded logic
            pass
        
        # Fallback logic
        if temperament_type == "Analytical":
            if "degree" in education.lower():
                adjustment += 0.3
            if any(level in education for level in ["Master's", "Doctoral", "Professional"]):
                adjustment += 0.2
        elif temperament_type == "Optimistic":
            if any(level in education for level in ["Bachelor's", "Master's"]):
                adjustment += 0.2
        
        return adjustment
    
    def _get_employment_weight_adjustment(self, temperament_type: str, employment: str) -> float:
        """Get employment-based weight adjustment for temperament."""
        try:
            # Get employment adjustments from config
            employment_adjustments = self.config.get('temperament_weight_adjustments', {}).get('employment_based', {})
            
            if temperament_type in employment_adjustments:
                if "Unemployed" in employment_adjustments[temperament_type] and "Unemployed" in employment:
                    return employment_adjustments[temperament_type]["Unemployed"]
                    
                if "Student" in employment_adjustments[temperament_type] and "Student" in employment:
                    return employment_adjustments[temperament_type]["Student"]
                    
                if "management_sales_law" in employment_adjustments[temperament_type] and any(job in employment for job in ["Manager", "Sales", "Lawyer"]):
                    return employment_adjustments[temperament_type]["management_sales_law"]
                    
                if "Retired" in employment_adjustments[temperament_type] and "Retired" in employment:
                    return employment_adjustments[temperament_type]["Retired"]
                    
                if "unemployment_disability" in employment_adjustments[temperament_type] and any(status in employment for status in ["Unemployed", "Disabled"]):
                    return employment_adjustments[temperament_type]["unemployment_disability"]
            
        except (KeyError, TypeError):
            # Fall back to hardcoded values
            pass
            
        # Fallback adjustments
        adjustments = {
            "Anxious": (0.5 if "Unemployed" in employment else 
                      0.2 if "Student" in employment else 0),
            "Aggressive": (0.2 if any(job in employment for job in ["Manager", "Sales", "Lawyer"]) 
                         else 0),
            "Laid-back": 0.4 if "Retired" in employment else 0,
            "Pessimistic": (0.3 if any(status in employment for status in ["Unemployed", "Disabled"]) 
                          else 0),
        }
        return adjustments.get(temperament_type, 0)
    
    def generate_dataset(self, num_people: int) -> List[Dict[str, str]]:
        """
        Generate a dataset of demographic information.
        
        Args:
            num_people (int): Number of people to generate.
            
        Returns:
            List[Dict[str, str]]: List of demographic records.
            
        Raises:
            ValueError: If num_people is not a positive integer.
        """
        if not isinstance(num_people, int) or num_people <= 0:
            raise ValueError("num_people must be a positive integer")
        
        return [self.generate_person() for _ in range(num_people)]
    
    def save_to_csv(self, num_people: int, filename: str, output_dir: str = ".") -> str:
        """
        Generate demographic data and save to CSV file.
        
        Args:
            num_people (int): Number of people to generate.
            filename (str): Name of the CSV file.
            output_dir (str): Directory to save the file. Defaults to current directory.
            
        Returns:
            str: Full path to the created CSV file.
            
        Raises:
            ValueError: If num_people is not positive or filename is empty.
            OSError: If unable to create output directory or write file.
        """
        if not isinstance(num_people, int) or num_people <= 0:
            raise ValueError("num_people must be a positive integer")
        
        if not filename or not filename.strip():
            raise ValueError("filename cannot be empty")
        
        # Generate the dataset
        dataset = self.generate_dataset(num_people)
        
        # Ensure output directory exists
        try:
            os.makedirs(output_dir, exist_ok=True)
        except OSError as e:
            raise OSError(f"Unable to create output directory '{output_dir}': {e}")
        
        # Create full file path
        if not filename.endswith('.csv'):
            filename += '.csv'
        filepath = os.path.join(output_dir, filename)
        
        # Write to CSV
        try:
            if dataset:
                fieldnames = dataset[0].keys()
                with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(dataset)
        except OSError as e:
            raise OSError(f"Unable to write CSV file '{filepath}': {e}")
        
        print(f"Generated {num_people} demographic records and saved to: {filepath}")
        return filepath
    
    def _load_street_names(self) -> List[str]:
        """
        Load street names from data/town_data.json if it exists.
        
        Returns:
            List[str]: List of street names, or empty list if file doesn't exist or can't be loaded.
        """
        try:
            # Get the path relative to the project root
            # This assumes the script is run from the project root or that data/town_data.json is accessible
            town_data_path = os.path.join("data", "town_data.json")
            
            # Also try absolute path from current working directory
            if not os.path.exists(town_data_path):
                # Try from the directory containing this script
                script_dir = os.path.dirname(os.path.abspath(__file__))
                # Go up to project root (assuming script is in src/utils/data/)
                project_root = os.path.dirname(os.path.dirname(os.path.dirname(script_dir)))
                town_data_path = os.path.join(project_root, "data", "town_data.json")
            
            if os.path.exists(town_data_path):
                with open(town_data_path, 'r', encoding='utf-8') as file:
                    town_data = json.load(file)
                    
                # Extract street names from the JSON structure
                street_names = []
                if 'streets' in town_data and isinstance(town_data['streets'], list):
                    for street in town_data['streets']:
                        if isinstance(street, dict) and 'name' in street:
                            street_names.append(street['name'])
                
                return street_names
                
        except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
            # Silently handle errors and fall back to default address generation
            pass
            
        return []
    
    def _generate_address_with_town_streets(self) -> str:
        """
        Generate an address using street names from town_data.json if available,
        otherwise fall back to Faker's default address generation.
        
        Returns:
            str: Generated address
        """
        if self.street_names:
            # Use a random street name from the loaded data
            street_name = random.choice(self.street_names)
            # Generate a house number
            house_number = random.randint(1, 999)
            # Generate the rest of the address using Faker
            city = self.fake.city()
            postcode = self.fake.postcode() if hasattr(self.fake, 'postcode') else self.fake.zipcode()
            
            # Construct the address
            address = f"{house_number} {street_name}, {city}, {postcode}"
            return address
        else:
            # Fall back to Faker's default address generation
            return self.fake.address().replace('\n', ', ')


def generate_demographic_csv(num_people: int, filename: str, output_dir: str = "data", locale: str = "en_US", seed: Optional[int] = None) -> str:
    """
    Convenience function for quick CSV generation of demographic data.
    
    Args:
        num_people (int): Number of people to generate.
        filename (str): Name of the CSV file.
        output_dir (str): Directory to save the file. Defaults to "data".
        locale (str): Faker locale to use for generation. Defaults to "en_US".
        seed (Optional[int]): Random seed for reproducible results.
        
    Returns:
        str: Full path to the created CSV file.
    """
    generator = PeopleGenerator(locale=locale, seed=seed)
    return generator.save_to_csv(num_people, filename, output_dir)


if __name__ == "__main__":
    # Load configuration
    config_path = os.path.join(os.path.dirname(__file__), 'people_config.yaml')
    defaults = {}
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            defaults = config.get('generation_defaults', {})
    except (FileNotFoundError, yaml.YAMLError) as e:
        print(f"Warning: Could not load people_config.yaml: {e}")
    
    # Define parameters for data generation, using config if available
    NUM_PEOPLE = defaults.get('num_people', 1000)
    OUTPUT_DIR = defaults.get('output_dir', "data")
    FILENAME = defaults.get('filename', "people_data.csv")
    LOCALE = defaults.get('locale', "en_GB")
    SEED = defaults.get('seed', 42)
    
    # Create the output directory if it doesn't exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print(f"Generating demographic data for {NUM_PEOPLE} people...")
    
    try:
        # Generate data and save to CSV
        filepath = generate_demographic_csv(
            num_people=NUM_PEOPLE,
            filename=FILENAME,
            output_dir=OUTPUT_DIR,
            locale=LOCALE,
            seed=SEED
        )
        
        print(f"Successfully generated data and saved to: {filepath}")
        print(f"Total records: {NUM_PEOPLE}")
        
    except Exception as e:
        print(f"Error generating data: {e}")
