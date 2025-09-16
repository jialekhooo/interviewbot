import os
import re
import json
import spacy
import pdfplumber
from docx import Document
from typing import Dict, Any, Optional, List
from datetime import datetime
import pytesseract
from PIL import Image
import io
import tempfile
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load English language model for NLP
nlp = spacy.load("en_core_web_sm")

class ResumeParser:
    """
    A class to parse resumes in various formats (PDF, DOCX, TXT) and extract structured information.
    """
    
    def __init__(self, file_path: str):
        """
        Initialize the ResumeParser with the path to the resume file.
        
        Args:
            file_path: Path to the resume file (PDF, DOCX, or TXT)
        """
        self.file_path = file_path
        self.file_extension = os.path.splitext(file_path)[1].lower()
        self.text = self._extract_text()
        self.doc = nlp(self.text) if self.text else None
        
    def _extract_text(self) -> str:
        """Extract text from the resume file based on its format."""
        try:
            if self.file_extension == '.pdf':
                return self._extract_text_from_pdf()
            elif self.file_extension == '.docx':
                return self._extract_text_from_docx()
            elif self.file_extension == '.txt':
                return self._extract_text_from_txt()
            else:
                logger.error(f"Unsupported file format: {self.file_extension}")
                return ""
        except Exception as e:
            logger.error(f"Error extracting text: {str(e)}")
            return ""
    
    def _extract_text_from_pdf(self) -> str:
        """Extract text from a PDF file."""
        text = ""
        try:
            with pdfplumber.open(self.file_path) as pdf:
                for page in pdf.pages:
                    # Try to extract text directly first
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                    else:
                        # Fallback to OCR if no text is found
                        try:
                            img = page.to_image()
                            img_bytes = io.BytesIO()
                            img.save(img_bytes, format='PNG')
                            img_bytes.seek(0)
                            page_text = pytesseract.image_to_string(Image.open(img_bytes))
                            text += page_text + "\n"
                        except Exception as e:
                            logger.warning(f"OCR failed for page: {str(e)}")
        except Exception as e:
            logger.error(f"Error reading PDF: {str(e)}")
            raise
        return text
    
    def _extract_text_from_docx(self) -> str:
        """Extract text from a DOCX file."""
        try:
            doc = Document(self.file_path)
            return "\n".join([paragraph.text for paragraph in doc.paragraphs])
        except Exception as e:
            logger.error(f"Error reading DOCX: {str(e)}")
            raise
    
    def _extract_text_from_txt(self) -> str:
        """Extract text from a TXT file."""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error reading TXT: {str(e)}")
            raise
    
    def parse(self) -> Dict[str, Any]:
        """
        Parse the resume and return structured data.
        
        Returns:
            Dict containing structured resume data
        """
        if not self.doc:
            return {}
            
        return {
            "name": self._extract_name(),
            "contact_info": self._extract_contact_info(),
            "education": self._extract_education(),
            "experience": self._extract_experience(),
            "skills": self._extract_skills(),
            "summary": self._extract_summary(),
            "raw_text": self.text
        }
    
    def _extract_name(self) -> str:
        """Extract the candidate's name from the resume."""
        # Look for name at the beginning of the document
        first_few_lines = self.text.strip().split('\n')[:10]
        for line in first_few_lines:
            line = line.strip()
            if line and len(line.split()) in [2, 3]:  # Most names are 2-3 words
                # Check if the line looks like a name (starts with capital letters)
                if line.istitle() and not any(word.lower() in ['email', 'phone', 'linkedin'] for word in line.split()):
                    return line
        return ""
    
    def _extract_contact_info(self) -> Dict[str, str]:
        """Extract contact information from the resume."""
        contact_info = {
            "email": "",
            "phone": "",
            "linkedin": "",
            "github": "",
            "portfolio": ""
        }
        
        # Extract email
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        email_match = re.search(email_pattern, self.text)
        if email_match:
            contact_info["email"] = email_match.group(0)
        
        # Extract phone number (various formats)
        phone_patterns = [
            r'\+?[\d\s-]{10,}',  # Matches +1 234 567 8901, 123-456-7890, etc.
            r'\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}'  # Matches (123) 456-7890
        ]
        
        for pattern in phone_patterns:
            phone_match = re.search(pattern, self.text)
            if phone_match:
                contact_info["phone"] = phone_match.group(0)
                break
        
        # Extract LinkedIn and GitHub profiles
        linkedin_pattern = r'linkedin\.com/in/[a-zA-Z0-9-]+'
        github_pattern = r'github\.com/[a-zA-Z0-9-]+'
        
        linkedin_match = re.search(linkedin_pattern, self.text.lower())
        if linkedin_match:
            contact_info["linkedin"] = f"https://{linkedin_match.group(0)}"
        
        github_match = re.search(github_pattern, self.text.lower())
        if github_match:
            contact_info["github"] = f"https://{github_match.group(0)}"
        
        # Extract portfolio website
        url_pattern = r'https?://(?:[\w-]+\.)+[a-z]{2,}(?:/[^\s]*)?'
        url_matches = re.finditer(url_pattern, self.text.lower())
        
        for match in url_matches:
            url = match.group(0)
            if 'linkedin' not in url and 'github' not in url and not contact_info["portfolio"]:
                contact_info["portfolio"] = url
        
        return contact_info
    
    def _extract_education(self) -> List[Dict[str, Any]]:
        """Extract education information from the resume."""
        education = []
        
        # Common education section headers
        edu_headers = [
            'education', 'academic background', 'educational background',
            'academic qualifications', 'academics', 'degrees'
        ]
        
        # Find the education section
        edu_section = self._find_section(edu_headers)
        if not edu_section:
            return education
        
        # Split into individual education entries
        entries = re.split(r'\n\s*\n', edu_section)
        
        for entry in entries:
            # Skip empty entries
            if not entry.strip():
                continue
                
            edu_entry = {
                'degree': '',
                'institution': '',
                'dates': '',
                'gpa': '',
                'description': ''
            }
            
            # Split into lines and process each line
            lines = [line.strip() for line in entry.split('\n') if line.strip()]
            
            if not lines:
                continue
                
            # First line typically contains degree and institution
            first_line = lines[0]
            edu_entry['institution'] = first_line
            
            # Look for degree in the first few lines
            degree_keywords = ['bachelor', 'master', 'phd', 'doctorate', 'bs', 'ms', 'ba', 'ma', 'b\.', 'm\.', 'ph\.d']
            for line in lines[:3]:
                if any(keyword in line.lower() for keyword in degree_keywords):
                    edu_entry['degree'] = line
                    break
            
            # Look for dates (e.g., 2015 - 2019, Sep 2018 - May 2022)
            date_pattern = r'(\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|May|June|July|August|September|October|November|December)[a-z]*[\s,.-]*(?:19|20)\d{2}[\s]*[-–—]?[\s]*(?:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|May|June|July|August|September|October|November|December)[a-z]*[\s,.-]*(?:19|20)\d{2}|Present|Current|Now)\b|\b(?:19|20)\d{2}[\s]*[-–—][\s]*(?:19|20)?\d{2}\b)'
            for line in lines:
                date_match = re.search(date_pattern, line, re.IGNORECASE)
                if date_match:
                    edu_entry['dates'] = date_match.group(0)
                    break
            
            # Look for GPA
            gpa_pattern = r'\bGPA[:\s]*([0-4]\.\d{1,2})\b|\b([0-4]\.\d{1,2})\s*GPA\b'
            for line in lines:
                gpa_match = re.search(gpa_pattern, line, re.IGNORECASE)
                if gpa_match:
                    edu_entry['gpa'] = gpa_match.group(1) or gpa_match.group(2)
                    break
            
            # The rest is description
            description_lines = []
            for line in lines:
                if not any([
                    line == edu_entry['institution'],
                    line == edu_entry['degree'],
                    line == edu_entry['dates'],
                    line == f"GPA: {edu_entry['gpa']}" if edu_entry['gpa'] else False
                ]):
                    description_lines.append(line)
            
            if description_lines:
                edu_entry['description'] = '\n'.join(description_lines)
            
            education.append(edu_entry)
        
        return education
    
    def _extract_experience(self) -> List[Dict[str, Any]]:
        """Extract work experience from the resume."""
        experience = []
        
        # Common experience section headers
        exp_headers = [
            'experience', 'work experience', 'professional experience',
            'employment history', 'work history', 'professional background'
        ]
        
        # Find the experience section
        exp_section = self._find_section(exp_headers)
        if not exp_section:
            return experience
        
        # Split into individual experience entries
        entries = re.split(r'\n\s*\n', exp_section)
        
        for entry in entries:
            # Skip empty entries
            if not entry.strip():
                continue
                
            exp_entry = {
                'title': '',
                'company': '',
                'dates': '',
                'location': '',
                'description': ''
            }
            
            # Split into lines and process each line
            lines = [line.strip() for line in entry.split('\n') if line.strip()]
            
            if not lines:
                continue
                
            # First line typically contains job title and company
            first_line = lines[0]
            exp_entry['title'] = first_line
            
            # Second line might contain company and dates/location
            if len(lines) > 1:
                second_line = lines[1]
                
                # Check if this line contains dates
                date_pattern = r'(\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|May|June|July|August|September|October|November|December)[a-z]*[\s,.-]*(?:19|20)\d{2}[\s]*[-–—]?[\s]*(?:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|May|June|July|August|September|October|November|December)[a-z]*[\s,.-]*(?:19|20)\d{2}|Present|Current|Now)\b|\b(?:19|20)\d{2}[\s]*[-–—][\s]*(?:19|20)?\d{2}\b)'
                date_match = re.search(date_pattern, second_line, re.IGNORECASE)
                
                if date_match:
                    exp_entry['dates'] = date_match.group(0)
                    # The rest is company and location
                    company_location = second_line.replace(exp_entry['dates'], '').strip()
                    
                    # Try to split company and location (common patterns)
                    if ' at ' in company_location:
                        parts = company_location.split(' at ', 1)
                        exp_entry['title'] = parts[0].strip()
                        company_location = parts[1].strip()
                    elif ' | ' in company_location:
                        parts = company_location.split(' | ', 1)
                        exp_entry['company'] = parts[0].strip()
                        exp_entry['location'] = parts[1].strip()
                    elif ', ' in company_location:
                        parts = company_location.split(', ')
                        exp_entry['company'] = parts[0].strip()
                        exp_entry['location'] = ', '.join(parts[1:]).strip()
                    else:
                        exp_entry['company'] = company_location
                else:
                    # No dates in the second line, treat as company/location
                    if ' | ' in second_line:
                        parts = second_line.split(' | ', 1)
                        exp_entry['company'] = parts[0].strip()
                        exp_entry['location'] = parts[1].strip()
                    elif ', ' in second_line:
                        parts = second_line.split(', ')
                        exp_entry['company'] = parts[0].strip()
                        exp_entry['location'] = ', '.join(parts[1:]).strip()
                    else:
                        exp_entry['company'] = second_line
            
            # The rest is description
            description_lines = []
            start_idx = 1 if len(lines) > 1 else 0
            
            for line in lines[start_idx:]:
                if not any([
                    line == exp_entry['title'],
                    line == exp_entry['company'],
                    line == exp_entry['dates'],
                    line == exp_entry['location']
                ]):
                    # Clean up bullet points
                    line = re.sub(r'^[•\-*]\s*', '', line)
                    description_lines.append(line)
            
            if description_lines:
                exp_entry['description'] = '\n'.join(description_lines)
            
            experience.append(exp_entry)
        
        return experience
    
    def _extract_skills(self) -> List[str]:
        """Extract skills from the resume."""
        skills = set()
        
        # Common skills section headers
        skill_headers = [
            'skills', 'technical skills', 'key skills', 'core competencies',
            'technical expertise', 'technologies', 'programming languages'
        ]
        
        # Find the skills section
        skill_section = self._find_section(skill_headers)
        if skill_section:
            # Extract skills from the skills section
            lines = [line.strip() for line in skill_section.split('\n') if line.strip()]
            
            for line in lines:
                # Split by common delimiters
                for item in re.split(r'[,;•\-*|]', line):
                    skill = item.strip()
                    if skill and len(skill) > 1:  # Skip empty or single-character items
                        skills.add(skill)
        
        # Also look for skills in the experience and projects sections
        sections_to_search = []
        
        # Experience section
        exp_headers = ['experience', 'work experience', 'professional experience']
        exp_section = self._find_section(exp_headers)
        if exp_section:
            sections_to_search.append(exp_section)
        
        # Projects section
        project_headers = ['projects', 'personal projects', 'academic projects']
        project_section = self._find_section(project_headers)
        if project_section:
            sections_to_search.append(project_section)
        
        # Common tech skills to look for
        common_tech_skills = [
            'python', 'javascript', 'java', 'c++', 'c#', 'ruby', 'php', 'swift', 'kotlin', 'go', 'rust',
            'html', 'css', 'sass', 'less', 'typescript', 'react', 'angular', 'vue', 'node.js', 'django',
            'flask', 'spring', 'rails', 'laravel', 'asp.net', 'sql', 'mysql', 'postgresql', 'mongodb',
            'redis', 'docker', 'kubernetes', 'aws', 'azure', 'gcp', 'git', 'jenkins', 'ansible', 'terraform',
            'machine learning', 'deep learning', 'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy',
            'data analysis', 'data visualization', 'tableau', 'power bi', 'big data', 'hadoop', 'spark'
        ]
        
        for section in sections_to_search:
            for skill in common_tech_skills:
                if re.search(r'\b' + re.escape(skill) + r'\b', section.lower()):
                    skills.add(skill)
        
        return sorted(list(skills))
    
    def _extract_summary(self) -> str:
        """Extract a summary/objective section from the resume."""
        # Common summary section headers
        summary_headers = [
            'summary', 'professional summary', 'career objective',
            'objective', 'about me', 'profile'
        ]
        
        # Find the summary section
        summary_section = self._find_section(summary_headers)
        if summary_section:
            return summary_section.strip()
        
        # If no explicit summary section, try to extract from the beginning of the document
        first_paragraph = self.text.strip().split('\n\n')[0]
        if len(first_paragraph.split()) > 20:  # Reasonable length for a summary
            return first_paragraph
        
        return ""
    
    def _find_section(self, possible_headers: List[str]) -> Optional[str]:
        """
        Find a section in the resume based on possible header names.
        
        Args:
            possible_headers: List of possible section header names
            
        Returns:
            The section content as a string, or None if not found
        """
        # Create a case-insensitive pattern for the headers
        pattern = r'(?i)^\s*(' + '|'.join(map(re.escape, possible_headers)) + r')\s*[\s:]*$'
        
        # Split the text into lines for processing
        lines = self.text.split('\n')
        
        # Find the start of the section
        start_idx = -1
        for i, line in enumerate(lines):
            if re.match(pattern, line.strip()):
                start_idx = i + 1
                break
        
        if start_idx == -1:
            return None
        
        # Find the end of the section (next section header or end of document)
        section_lines = []
        section_header_pattern = r'^\s*([A-Z][A-Za-z ]+)\s*[\s:]*$'
        
        for line in lines[start_idx:]:
            # Skip empty lines at the beginning
            if not section_lines and not line.strip():
                continue
                
            # Check if we've reached the next section
            if re.match(section_header_pattern, line):
                break
                
            section_lines.append(line)
        
        # Clean up the section text
        section_text = '\n'.join(section_lines).strip()
        
        # Remove any trailing section headers that might have been included
        for header in possible_headers:
            if section_text.endswith(header):
                section_text = section_text[:-len(header)].strip()
        
        return section_text if section_text else None

def parse_resume(file_path: str) -> Dict[str, Any]:
    """
    Parse a resume file and return structured data.
    
    Args:
        file_path: Path to the resume file (PDF, DOCX, or TXT)
        
    Returns:
        Dictionary containing structured resume data
    """
    try:
        parser = ResumeParser(file_path)
        return parser.parse()
    except Exception as e:
        logger.error(f"Error parsing resume: {str(e)}")
        return {"error": f"Failed to parse resume: {str(e)}"}

# Example usage
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python resume_parser.py <path_to_resume>")
        sys.exit(1)
    
    resume_path = sys.argv[1]
    if not os.path.exists(resume_path):
        print(f"Error: File not found: {resume_path}")
        sys.exit(1)
    
    result = parse_resume(resume_path)
    print(json.dumps(result, indent=2))
