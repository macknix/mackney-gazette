"""
Daily Article Generator

This module generates a configurable number of daily news articles for the Mackney Gazette.
It uses the article generation functionality from generate_article.py and configuraton
from articles_daily_config.yaml.

Usage:
    python -m src.generate_articles_daily [--config CONFIG_PATH]

Parameters:
    --config: Optional path to configuration file (defaults to articles_daily_config.yaml in project root)
"""

import os
import yaml
import argparse
import time
import shutil
import pandas as pd
from pathlib import Path
from typing import Optional, Dict, Any, List
import datetime

# Import the article generation functions
from src.utils.data.generate_article import create_new_story, continue_existing_story


def generate_articles_daily(config_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Generate daily articles based on configuration.

    Args:
        config_path: Path to the configuration file. If None, uses default.

    Returns:
        List of generated article data
    """
    # Use default config path if none provided
    if config_path is None:
        # Look for config in project root directory
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(project_root, "articles_daily_config.yaml")

    # Load configuration
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)

    # Extract configuration values
    article_count = config["articles"]["count"]
    backup_before_save = config["articles"]["save_options"]["backup_before_save"]
    article_limit = config["articles"]["save_options"]["article_limit"]
    
    # Story continuation configuration
    story_continuation_config = config["articles"].get("story_continuation", {})
    continuation_count = story_continuation_config.get("count", 0)
    generate_continuations_first = story_continuation_config.get("generate_first", True)
    max_continuation_attempts = story_continuation_config.get("max_attempts", 5)

    # Display configuration
    print(f"====== DAILY ARTICLE GENERATION - {datetime.datetime.now().strftime('%Y-%m-%d')} ======")
    print(f"Generating {article_count} new articles")
    if continuation_count > 0:
        print(f"Generating {continuation_count} story continuations")
        print(f"Generate continuations first: {generate_continuations_first}")
    
    print(f"Total articles to generate: {article_count + continuation_count}")

    # Backup articles.csv if enabled
    if backup_before_save:
        data_dir = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) / 'data'
        articles_csv = data_dir / 'articles.csv'
        
        if articles_csv.exists():
            backup_file = data_dir / f'articles.csv.bak'
            shutil.copy2(articles_csv, backup_file)
            print(f"Backed up articles file to {backup_file}")

    generated_articles = []
    successful_continuations = 0
    
    # Generate story continuations if configured
    if continuation_count > 0:
        print(f"\n=== STORY CONTINUATION PHASE ===")
        
        successful_continuations = 0
        attempts = 0
        
        while successful_continuations < continuation_count and attempts < max_continuation_attempts:
            attempts += 1
            print(f"\n--- Continuation attempt {attempts} (targeting {successful_continuations + 1} of {continuation_count}) ---")
            
            try:
                # Generate continuation article
                continuation_article = continue_existing_story()
                
                if continuation_article:
                    generated_articles.append(continuation_article)
                    successful_continuations += 1
                    print(f"Successfully generated continuation {successful_continuations} of {continuation_count}")
                    
                    # Add a small delay between continuations
                    if successful_continuations < continuation_count:
                        time.sleep(2)
                else:
                    print("No eligible stories found for continuation")
                    # If no stories are available, break early
                    break
                    
            except Exception as e:
                print(f"Error generating continuation {attempts}: {e}")
        
        print(f"\n=== Story Continuation Summary ===")
        print(f"Successfully generated {successful_continuations} of {continuation_count} continuations")
        print(f"Total attempts: {attempts}")
        
        # Adjust the new article count based on successful continuations
        if successful_continuations < continuation_count:
            shortage = continuation_count - successful_continuations
            print(f"Shortage of {shortage} continuations - will generate {shortage} additional new articles")
            article_count += shortage

    # Generate new articles
    print(f"\n=== NEW ARTICLE GENERATION PHASE ===")
    new_articles_generated = 0
    
    for i in range(article_count):
        print(f"\n--- Generating new article {i+1} of {article_count} ---")
        try:
            # Generate article
            article = create_new_story()
            generated_articles.append(article)
            new_articles_generated += 1
            
            # Add a small delay between articles to avoid rate limiting issues
            if i < article_count - 1:
                time.sleep(1)
                
        except Exception as e:
            print(f"Error generating new article {i+1}: {e}")

    print(f"\n=== FINAL GENERATION SUMMARY ===")
    print(f"Story continuations: {successful_continuations if continuation_count > 0 else 0}")
    print(f"New articles: {new_articles_generated}")
    print(f"Total articles generated: {len(generated_articles)}")
    print(f"Target total: {continuation_count + article_count}")

    # Prune old articles if limit is set
    if article_limit > 0:
        try:
            data_dir = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) / 'data'
            articles_csv = data_dir / 'articles.csv'
            
            if articles_csv.exists():
                # Read existing articles
                articles_df = pd.read_csv(articles_csv)
                
                # Check if we have more than the limit
                if len(articles_df) > article_limit:
                    # Sort by publication date and last_updated (newest first)
                    articles_df['last_updated'] = pd.to_datetime(articles_df['last_updated'])
                    articles_df = articles_df.sort_values(by='last_updated', ascending=False)
                    
                    # Keep only the newest articles up to the limit
                    articles_df = articles_df.head(article_limit)
                    
                    # Save the pruned dataframe
                    articles_df.to_csv(articles_csv, index=False)
                    print(f"Pruned articles.csv to keep the {article_limit} most recent articles")
        except Exception as e:
            print(f"Error pruning old articles: {e}")

    return generated_articles


def main():
    """
    Main function to run the daily article generation.
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Generate daily articles")
    parser.add_argument("--config", help="Path to configuration file", default=None)
    args = parser.parse_args()
    
    # Generate articles
    generate_articles_daily(args.config)


if __name__ == "__main__":
    main()
