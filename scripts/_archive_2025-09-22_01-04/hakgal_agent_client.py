# HAK/GAL Agent Client - Erstellt von Gemini AI
# Für die Integration anderer LLM-Agents mit dem HAK/GAL MCP System

import requests
import json

class HAKGALAgentClient:
    def __init__(self, api_key, write_token):
        self.api_key = api_key
        self.write_token = write_token
        self.api_base = "http://127.0.0.1:5002"
        self.headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }

    def delegate_task(self, target_agent, task_description, context):
        """Delegates a task to another agent."""
        url = f"{self.api_base}/api/agent-bus/delegate"
        payload = {
            "target_agent": target_agent,
            "task_description": task_description,
            "context": context
        }
        params = {"auth_token": self.write_token}
        
        try:
            response = requests.post(url, headers=self.headers, json=payload, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error delegating task: {e}")
            return None

    def get_facts_count(self):
        """Retrieves the number of facts."""
        url = f"{self.api_base}/api/facts/count"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error getting facts count: {e}")
            return None

    def get_governor_status(self):
        """Retrieves the governor's status."""
        url = f"{self.api_base}/api/governor/status"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error getting governor status: {e}")
            return None

# Beispiel-Verwendung:
if __name__ == "__main__":
    # HAK/GAL Credentials
    api_key = "hg_sk_4f9a8e1b7d2c5f6a8b3d9e0c1a7b4f9d"
    write_token = "515f57956e7bd15ddc3817573598f190"
    
    client = HAKGALAgentClient(api_key, write_token)
    
    # Test: Task delegieren
    task_result = client.delegate_task(
        target_agent="gemini",
        task_description="Teste die Agent-Integration",
        context={"test": True, "agent": "client_test"}
    )
    print(f"Task result: {task_result}")
    
    # Test: Facts Count
    facts_count = client.get_facts_count()
    print(f"Facts count: {facts_count}")
    
    # Test: Governor Status
    governor_status = client.get_governor_status()
    print(f"Governor status: {governor_status}")