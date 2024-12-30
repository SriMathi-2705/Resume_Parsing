from pdfminer.high_level import extract_text
import spacy
from spacy.matcher import Matcher
import re
from datetime import datetime, date


class ResumeParser:

    @staticmethod
    def extract_text_from_pdf(pdf_path):
        """
        Extracts text from a PDF file.
        """
        return extract_text(pdf_path)

    @staticmethod
    def extract_name(resume_text):
        """
        Extracts the name from the resume text, focusing on names with initials
        and simple two-word names. Uses spaCy's Matcher for structured patterns
        and a regex fallback for additional formats.
        """
        nlp = spacy.load("en_core_web_sm")
        matcher = Matcher(nlp.vocab)

        # Define patterns for names with initials and simple two-word names
        two_word_name_pattern = [[{"POS": "PROPN"}, {"POS": "PROPN"}]]
        initial_name_pattern = [
            [
                {"IS_ALPHA": True, "IS_TITLE": True},
                {"TEXT": {"REGEX": "^[A-Z]\.?$"}},
                {"IS_ALPHA": True, "IS_TITLE": True},
            ]
        ]

        # Add patterns to matcher
        matcher.add("TWO_WORD_NAME", two_word_name_pattern)
        matcher.add("INITIAL_NAME", initial_name_pattern)

        doc = nlp(resume_text)
        matches = matcher(doc)

        # Exclusion terms to prevent non-name sections from being captured
        exclusion_terms = {"curriculum vitae", "resume", "cv"}

        # Check for matches using matcher patterns
        for match_id, start, end in matches:
            name_candidate = doc[start:end].text
            if name_candidate.lower() not in exclusion_terms:
                return name_candidate

        # Regex Fallback: Supports initials and simple two-word names
        regex_pattern = r"\b([A-Z][a-z]+(?:\s[A-Z]\.?\s)?[A-Z][a-z]+)\b"
        regex_match = re.search(regex_pattern, resume_text)

        if regex_match:
            name_candidate = regex_match.group()
            if name_candidate.lower() not in exclusion_terms:
                return name_candidate

        return None  # Return None if no name is found

    @staticmethod
    def extract_email_from_resume(text):
        """
        Extracts email addresses from the resume text using regex.
        Gives priority to structured format `Email: value`.
        """
        structured_email_pattern = (
            r"Email\s*:\s*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})"
        )
        match = re.search(structured_email_pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)

        # General email pattern
        general_email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
        match = re.search(general_email_pattern, text)
        return match.group() if match else None

    @staticmethod
    def extract_mobile_number(text):
        # """
        # Extracts phone numbers, with priority to structured format `Phone: value`.
        # """
        # structured_phone_pattern = r"Phone\s*:\s*(\+?\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9})"

        # match = re.search(structured_phone_pattern, text, re.IGNORECASE)
        # if match:
        #     return match.group(1)

        # # General phone number pattern
        # general_phone_pattern = r"(?:\+91[-\s]?\d{10}|\d{10}|\d{5}[-\s]?\d{5})"
        # match = re.search(general_phone_pattern, text)
        # return match.group() if match else None
        pass
    
    @staticmethod
    def extract_mobile_numbers(text, max_numbers=3):
        """
        Extracts up to `max_numbers` phone numbers from text, prioritizing 
        structured format 'Phone: value' when available, allows 10- or 
        11-digit numbers, and adds '+91' if a country code is missing.
        """
        # Priority pattern: Structured format "Phone: value"
        structured_phone_pattern = r"Phone\s*:\s*(\+?\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}[-.\s]?\d{3,4})"
        
        # General pattern: Common phone formats, including 10 or 11-digit options
        general_phone_pattern = r"\b(?:\+91[-\s]?\d{10}|\d{11}|\d{10}|\d{3}[-\s]?\d{3}[-\s]?\d{4}|\d{5}[-\s]?\d{5})\b"

        # Find all structured phone numbers first
        structured_matches = re.findall(structured_phone_pattern, text, re.IGNORECASE)
        
        # If we found fewer than `max_numbers` structured matches, search with the general pattern
        if len(structured_matches) < max_numbers:
            general_matches = re.findall(general_phone_pattern, text)
            
            # Combine structured and general matches
            matches = structured_matches + general_matches
        else:
            matches = structured_matches

        # Remove duplicates and limit to `max_numbers`
        unique_matches = list(dict.fromkeys(matches))[:max_numbers]

        # Add '+91' if the country code is missing
        formatted_numbers = [
            f"+91{number}" if not number.startswith("+") else number
            for number in unique_matches
        ]

        return formatted_numbers




    @staticmethod
    def extract_education_from_resume(text):
        """
        Extracts education details using regex patterns.
        """
        education_pattern = r"(?i)(?:Diploma|Dip\.\w+|\bB\.\w+|\bM\.\w+|\bPh\.D|\bBachelor(?:'s)?|\bMasters(?:'s)?|\bB\.Tech|\bM\.Tech|\bB\.E\.|\bM\.E\.|\bB\.Sc|\bM\.Sc|\bB\.Com|\bM\.Com)\s(?:\w+\s)*\w+"
        return re.findall(education_pattern, text)

    @staticmethod
    def extract_gender_from_resume(text):
        """
        Extracts gender from the resume text, with priority to structured format `Gender: value`.
        """
        structured_gender_pattern = r"Gender\s*:\s*(Male|Female)"
        match = re.search(structured_gender_pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).capitalize()

        gender_pattern = r"\b(Male|Female)\b"
        match = re.search(gender_pattern, text, re.IGNORECASE)
        return match.group(0).capitalize() if match else None

    @staticmethod
    def extract_experience_from_resume(text):
        """
        Extracts years of experience from the resume text using regex.
        Priority is given to structured format `Experience: value`.
        """
        structured_experience_pattern = r"Experience\s*:\s*(\d+)\s*(?:years?|yrs?)"
        match = re.search(structured_experience_pattern, text, re.IGNORECASE)
        if match:
            return f"{match.group(1)} yrs"

        experience_pattern = r"(\d+)\s*(?:years?|months?)\s*(?:of)?\s*(?:experience)?"
        match = re.search(experience_pattern, text, re.IGNORECASE)
        return match.group(0) if match else None

    @staticmethod
    def extract_dob_age(text):
        """
        Extracts date of birth and age if found in structured format.
        If structured formats are absent, it uses regex and NLP to parse dates.
        """
        dob, age = None, None

        structured_dob_pattern = r"(?:DOB|Date\s*of\s*Birth|D.O.B)\s*:\s*(.*)"
        structured_age_pattern = r"Age\s*:\s*(\d+)"
        dob_match = re.search(structured_dob_pattern, text, re.IGNORECASE)
        age_match = re.search(structured_age_pattern, text, re.IGNORECASE)

        if dob_match:
            dob = ResumeParser.parse_date(dob_match.group(1).strip())
        if age_match:
            age = int(age_match.group(1))

        if not dob:
            nlp = spacy.load("en_core_web_sm")
            doc = nlp(text)
            for ent in doc.ents:
                if ent.label_ == "DATE":
                    dob = ResumeParser.parse_date(ent.text)
                    if dob:
                        break

        if not age:
            age_pattern = re.search(
                r"\b(?:age|aged)\s*[:\-]?\s*(\d{1,2})\b", text, re.IGNORECASE
            )
            if age_pattern:
                age = int(age_pattern.group(1))

        if dob and not age:
            age = ResumeParser.calculate_age(dob)

        return dob, age

    @staticmethod
    def remove_ordinal_suffix(date_str):
        """
        Removes ordinal suffixes (e.g., 1st, 2nd) from date strings.
        """
        return re.sub(r"(\d+)(st|nd|rd|th)", r"\1", date_str)

    @staticmethod
    def parse_date(date_str):
        """
        Parses date strings using multiple formats.
        """
        date_str = ResumeParser.remove_ordinal_suffix(date_str)
        formats = [
            "%d %B %Y",
            "%d-%b-%Y",
            "%d %b %Y",
            "%d-%B-%Y",
            "%d/%m/%Y",
            "%d-%m-%Y",
            "%Y-%m-%d",
            "%d,%B,%Y",
            "%d %b%Y",
            "%d:%b:%Y",
            "%d:%B:%Y",
        ]
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        return None

    @staticmethod
    def calculate_age(dob):
        """
        Calculates age from date of birth.
        """
        today = datetime.today().date()
        return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

    @staticmethod
    def format_date_to_custom(date_input):
        # Return None if the input is None
        if date_input is None:
            return None

        # If the input is a datetime.date (but not a datetime), convert it to datetime
        if isinstance(date_input, date) and not isinstance(date_input, datetime):
            date_obj = datetime.combine(date_input, datetime.min.time())
        elif isinstance(date_input, datetime):
            date_obj = date_input
        else:
            # Parse the string input assuming it's in 'YYYY-MM-DD' format
            date_obj = datetime.strptime(
                date_input, "%Y-%m-%d"
            )  # Adjust format if needed

        # Format to the desired output format
        return date_obj.strftime("%d-%b-%Y")

    @staticmethod
    def parse_resume(pdf_path):
        """
        Main method to parse resume from PDF and return extracted details.
        """
        text = ResumeParser.extract_text_from_pdf(pdf_path)
        name = ResumeParser.extract_name(text)
        email = ResumeParser.extract_email_from_resume(text)
        phone = ResumeParser.extract_mobile_numbers(text)
        education = ResumeParser.extract_education_from_resume(text)
        dob, age = ResumeParser.extract_dob_age(text)
        gender = ResumeParser.extract_gender_from_resume(text)
        experience = ResumeParser.extract_experience_from_resume(text)
        date_of_birth = ResumeParser.format_date_to_custom(dob)
        return {
            "name": name,
            "email": email,
            "phone": phone,
            "education": education,
            # "dob": dob,
            "date of birth ": date_of_birth,
            "age": age,
            "gender": gender,
            "experience": experience,
        }



