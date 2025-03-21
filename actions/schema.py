from typing import Any, Dict, List

class MessageDatePicker:
    """
    Represents a date picker component in a message schema.
    
    Attributes:
        type (str): The type of the component, always "date_picker".
        title (str): The title of the date picker.
        value (str): The default or selected date value.
    """
    def __init__(self, title: str, value: str = "", format_payload: str = "YYYY-MM-DD"):
        self.type = "date_picker"
        self.title = title
        self.value = value
        self.format_payload = format_payload

    def to_dict(self) -> Dict[str, Any]:
        """Converts the date picker object to a dictionary format."""
        return {    
            "type": self.type,
            "content": {
                "title": self.title,
                "value": self.value,
                "payload_template": self.format_payload
            }
        }
    
class MessageRangePicker:
    """
    Represents a range picker component in a message schema.
    
    Attributes:
        type (str): The type of the component, always "range_picker".
        title (str): The title of the range picker.
        value (str): The default or selected range value.
    """
    def __init__(self, title: str, value: str = "", format_payload: str = "YYYY-MM-DD - YYYY-MM-DD"):
        self.type = "range_picker"
        self.title = title
        self.value = value
        self.format_payload = format_payload

    def to_dict(self) -> Dict[str, Any]:
        """Converts the range picker object to a dictionary format."""
        return {
            "type": self.type,
            "content": {
                "start":{
                    "title": self.title,
                    "value": self.value,
                },
                "end":{
                    "title": self.title,
                    "value": self.value,
                },
                "payload_template": self.format_payload
            }   
        }
    
class MessageSelectOptions:
    """
    Represents a select dropdown component in a message schema.
    
    Attributes:
        type (str): The type of the component, always "select".
        title (str): The title of the select dropdown.
        options (List[Dict[str, Any]]): A list of available options label,value.
    """
    def __init__(self, title: str, options: List[Dict[str, Any]]):
        self.type = "select"
        self.title = title
        self.options = options

    def options_to_dict(self):
        """Converts the select options object to a dictionary format."""
        return [{"label": option["label"], "value": option["value"]} for option in self.options]


    def to_dict(self) -> Dict[str, Any]:
        """Converts the select options object to a dictionary format."""
        return {
            "type": self.type,
            "content": {
                "title": self.title,
                "options": self.options,
            }
        }
    
class MessageSchema:
    """
    Represents a structured message schema containing multiple components.
    
    Attributes:
        sender_type (str): The type of sender.
        obj (List[Any]): A list of message components.
    """
    def __init__(self, sender_type: str):
        self.sender_type = sender_type
        self.obj = []
    
    def add_date_picker(self, date_picker: MessageDatePicker) -> "MessageSchema":
        """Adds a date picker component to the message schema."""
        self.obj.append(date_picker)
        return self
    
    def add_range_picker(self, range_picker: MessageRangePicker) -> "MessageSchema":
        """Adds a range picker component to the message schema."""
        self.obj.append(range_picker)
        return self
    
    def add_select(self, select: MessageSelectOptions) -> "MessageSchema":
        """Adds a select options component to the message schema."""
        self.obj.append(select)
        return self

    def to_dict(self) -> Dict[str, Any]:
        """Converts the message schema object to a dictionary format."""
        return {
            "sender_type": self.sender_type,
            "components": [option.to_dict() for option in self.obj]
        }
