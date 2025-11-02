"""Test script for resume export functionality"""

from app.utils.resume_export import generate_resume_pdf, generate_resume_docx

# Sample resume text
sample_resume = """
JOHN DOE
========

PROFESSIONAL SUMMARY
-------------------
Motivated Computer Science student with a strong foundation in technical and analytical skills.
Proven ability to apply theoretical knowledge in practical settings through internship experience.

EDUCATION
---------
Bachelor of Science in Computer Science
XYZ University, 2020-2024
GPA: 3.8/4.0

TECHNICAL SKILLS
---------------
- Programming Languages: Python, JavaScript, Java, C++
- Web Development: React, Node.js, FastAPI, HTML/CSS
- Databases: PostgreSQL, MongoDB
- Tools: Git, Docker, AWS

PROFESSIONAL EXPERIENCE
----------------------
Software Engineering Intern
ABC Company, Summer 2023
- Developed and maintained web applications using React and FastAPI
- Collaborated with cross-functional teams to deliver features on time
- Improved application performance by 30% through code optimization

ACHIEVEMENTS & INTERESTS
-----------------------
- Dean's List (2021-2023)
- Hackathon Winner - Best Technical Solution
- Open source contributor
- Passionate about AI and machine learning
"""

def test_pdf_generation():
    """Test PDF generation"""
    print("Testing PDF generation...")
    try:
        pdf_content = generate_resume_pdf(sample_resume, "John Doe")
        
        # Save to file for manual inspection
        with open("test_output_resume.pdf", "wb") as f:
            f.write(pdf_content)
        
        print(f"✓ PDF generated successfully! Size: {len(pdf_content)} bytes")
        print("✓ Saved as: test_output_resume.pdf")
        return True
    except Exception as e:
        print(f"✗ PDF generation failed: {e}")
        return False


def test_docx_generation():
    """Test DOCX generation"""
    print("\nTesting DOCX generation...")
    try:
        docx_content = generate_resume_docx(sample_resume, "John Doe")
        
        # Save to file for manual inspection
        with open("test_output_resume.docx", "wb") as f:
            f.write(docx_content)
        
        print(f"✓ DOCX generated successfully! Size: {len(docx_content)} bytes")
        print("✓ Saved as: test_output_resume.docx")
        return True
    except Exception as e:
        print(f"✗ DOCX generation failed: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("Resume Export Test Suite")
    print("=" * 60)
    
    pdf_success = test_pdf_generation()
    docx_success = test_docx_generation()
    
    print("\n" + "=" * 60)
    print("Test Results:")
    print("=" * 60)
    print(f"PDF Generation: {'✓ PASSED' if pdf_success else '✗ FAILED'}")
    print(f"DOCX Generation: {'✓ PASSED' if docx_success else '✗ FAILED'}")
    
    if pdf_success and docx_success:
        print("\n✓ All tests passed! Check the generated files:")
        print("  - test_output_resume.pdf")
        print("  - test_output_resume.docx")
    else:
        print("\n✗ Some tests failed. Check error messages above.")
