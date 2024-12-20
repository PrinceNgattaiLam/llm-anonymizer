from enum import Enum
from pydantic import BaseModel
import yaml
from pathlib import Path
from typing import List, Optional, Tuple, Union
from dotenv import load_dotenv
from litellm import completion
from faker import Faker
fake = Faker()
import json
load_dotenv()

class Name(BaseModel):
    """Name, Firstname or surname of a person"""
    name: str
    def get_anonymized(self) -> str:
        return fake.name()

    def get_value(self) -> str:
        return self.name

class Email(BaseModel):
    """Email address"""
    email: str
    
    def get_anonymized(self) -> str:
        return fake.email()
    
    def get_value(self) -> str:
        return self.email

class Address(BaseModel):
    """Postal address"""
    address: str
    def get_anonymized(self) -> str:
        return fake.address()
    
    def get_value(self) -> str:
        return self.address
    
class PhoneNumber(BaseModel):
    """Phone number"""
    phone_numbers: str
    def get_anonymized(self) -> str:
        return fake.phone_number()
    
    def get_value(self) -> str:
        return self.phone_numbers
    
class Entities(BaseModel):
    entities: List[Union[Name, Email, PhoneNumber, Address]]

import os
class TextAnonymizer:
    def __init__(self, model_id):
        self.model_id = model_id
        self.entities = None
        self.anonymized_content = None
        self.anonym_entity_map = None
    
    def detect_entities(self):
        # Set self.entities to None
        self.entities = None
        resp = completion(
            model=f"{self.model_id}",
            temperature=0.1,
            top_p=0.1,
            messages=self.messages,
            response_format=Entities
        )
        parsed = resp.choices[0].message.content
        print(json.loads(parsed))
        self.entities = Entities(**json.loads(parsed))
    
    def get_anonymize_entities(self):
        if self.entities is None:
            print("No entities detected. Please call detect_entities() first.")
            return
        self.anonym_entity_map = {}
        for entity in self.entities.entities:
            self.anonym_entity_map[entity.get_value()] = entity.get_anonymized()
    
    def anonymize_content(self):
        if self.entities is None or self.anonym_entity_map is None:
            return
        self.anonymized_content = self.content
        for entity, anonym_entity in self.anonym_entity_map.items():
            print(f"Anonymizing {entity} to {anonym_entity}")
            self.anonymized_content = self.anonymized_content.replace(entity, anonym_entity)
        
    def run(self, input_file, output_file):
        with open(input_file, 'r') as file:
            self.content = file.read()
        self.messages = [
            {"role": "system", "content": "You are an assistant with the task of extracting entities from a provided content as input."},
            {"role": "user", "content": f"Here is the content: {self.content}"},]
        self.detect_entities()
        self.get_anonymize_entities()
        self.anonymize_content()
        with open(output_file, 'w') as file:
            file.write(self.anonymized_content)
        
if __name__ == "__main__":
    anonym = TextAnonymizer("openai/gpt-4o")
    anonym.run("input.txt", "output.txt")