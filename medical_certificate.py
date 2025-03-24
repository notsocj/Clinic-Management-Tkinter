import tkinter as tk
from tkinter import ttk, font, messagebox
from datetime import datetime
import tkinter.scrolledtext as scrolledtext
import os
import tempfile
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
import subprocess

class MedicalCertificateWindow:
    def __init__(self, parent, patient_data=None):
        self.window = tk.Toplevel(parent)
        self.window.title("Medical Certificate")
        self.window.geometry("800x600")
        self.window.configure(bg="#f0f0f0")
        
        # Parent reference
        self.parent = parent
        
        # Patient data should include name, age, address, findings, remarks
        self.patient_data = patient_data or {
            "name": "", 
            "age": "", 
            "address": "", 
            "findings": "",
            "remarks": ""
        }
        
        self.create_widgets()
        self.generate_medical_certificate()
        
    def create_widgets(self):
        # Main frame
        main_frame = tk.Frame(self.window, bg="#f0f0f0")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Rich text box with scrollbar
        self.rich_text = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, width=80, height=30)
        self.rich_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Button frame
        button_frame = tk.Frame(self.window, bg="#f0f0f0")
        button_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        # Print button
        self.print_button = ttk.Button(button_frame, text="Print Certificate", command=self.print_certificate)
        self.print_button.pack(side=tk.LEFT, padx=5)
        
        # PDF Print button - new button for generating and printing PDF
        self.pdf_button = ttk.Button(button_frame, text="Print as PDF", command=self.print_as_pdf)
        self.pdf_button.pack(side=tk.LEFT, padx=5)
        
        # Exit button
        self.exit_button = ttk.Button(button_frame, text="Close", command=self.window.destroy)
        self.exit_button.pack(side=tk.RIGHT, padx=5)
    
    def print_certificate(self):
        # Get content from the rich text widget
        content = self.rich_text.get("1.0", tk.END)
        
        # Create a temporary file
        fd, path = tempfile.mkstemp(suffix='.txt')
        try:
            with os.fdopen(fd, 'w') as temp:
                temp.write(content)
            
            # Open the file with the default application and print
            if os.name == 'nt':  # Windows
                os.startfile(path, "print")
            else:  # macOS and Linux
                subprocess.call(['lpr', path])
                
            messagebox.showinfo("Print", "Certificate sent to printer.")
        except Exception as e:
            messagebox.showerror("Print Error", f"Failed to print: {str(e)}")
        finally:
            # Clean up the temp file after a delay
            self.window.after(10000, lambda: os.unlink(path))
    
    def print_as_pdf(self):
        """Generate a PDF and send it to the printer"""
        try:
            # Create a temporary PDF file
            fd, pdf_path = tempfile.mkstemp(suffix='.pdf')
            os.close(fd)
            
            # Get the certificate content
            content = self.rich_text.get("1.0", tk.END)
            
            # Create a PDF document with A4 size
            doc = SimpleDocTemplate(pdf_path, pagesize=A4,
                                   rightMargin=72, leftMargin=72,
                                   topMargin=72, bottomMargin=72)
            
            # Styles for different text parts
            styles = getSampleStyleSheet()
            title_style = styles['Title']
            normal_style = styles['Normal']
            
            # Custom styles
            header_style = ParagraphStyle(
                'HeaderStyle',
                parent=styles['Heading1'],
                fontSize=16,
                textColor=colors.blue,
                spaceAfter=12
            )
            
            certification_style = ParagraphStyle(
                'CertificationStyle',
                parent=styles['Heading2'],
                fontSize=14,
                alignment=1,  # Center alignment
                spaceAfter=12
            )
            
            # Elements to add to the PDF
            elements = []
            
            # Add doctor's header
            elements.append(Paragraph("DR. BELINDA O. CABAUATAN", header_style))
            elements.append(Paragraph("ADULT NEUROLOGY", styles['Heading3']))
            elements.append(Paragraph("BRAIN, SPINAL CORD, NERVE AND MUSCLE SPECIALIST", styles['Heading4']))
            elements.append(Spacer(1, 12))
            
            # Add medical certificate title
            elements.append(Paragraph("MEDICAL CERTIFICATE", certification_style))
            elements.append(Spacer(1, 12))
            
            # Get today's date
            today_date = datetime.now().strftime("%A, %d %B %Y")
            
            # Add patient information
            patient_text = f"This is to certify that {self.patient_data['name']} {self.patient_data['age']} years old, from {self.patient_data['address']} was seen and examined in this clinic on {today_date}."
            elements.append(Paragraph(patient_text, normal_style))
            elements.append(Spacer(1, 12))
            
            # Add diagnosis
            elements.append(Paragraph("DIAGNOSIS:", styles['Heading3']))
            elements.append(Paragraph(self.patient_data.get('findings', 'No findings recorded'), normal_style))
            elements.append(Spacer(1, 24))
            
            # Add remarks section with the text from remarks data
            elements.append(Paragraph("REMARKS:", styles['Heading3']))
            if self.patient_data.get('remarks'):
                elements.append(Paragraph(self.patient_data.get('remarks'), normal_style))
            else:
                elements.append(Spacer(1, 48))  # Space for writing remarks
            
            # Add certification notice
            elements.append(Spacer(1, 24))
            elements.append(Paragraph("This certification is issued for reference use only.", normal_style))
            elements.append(Paragraph(f"Issued this {today_date} at Iriga Clinic.", normal_style))
            
            # Add space for signature
            elements.append(Spacer(1, 48))
            
            # Add doctor's information with right alignment
            doctor_style = ParagraphStyle(
                'DoctorStyle',
                parent=styles['Normal'],
                alignment=2  # Right alignment
            )
            elements.append(Paragraph("DR. BELINDA O. CABAUATAN M.D.", doctor_style))
            elements.append(Paragraph("NEUROLOGY", doctor_style))
            elements.append(Paragraph("Lic. No.    109769", doctor_style))
            elements.append(Paragraph("PTR. No.    4813787", doctor_style))
            
            # Build the PDF
            doc.build(elements)
            
            # Open with Chrome
            try:
                chrome_path = 'C:/Program Files/Google/Chrome/Application/chrome.exe'
                if os.path.exists(chrome_path):
                    subprocess.Popen([chrome_path, '--new-window', pdf_path])
                else:
                    # Fallback to default method
                    os.startfile(pdf_path)
                    
            except Exception as e:
                messagebox.showerror("Error", 
                    "Could not open PDF. Please check if Chrome is installed.")
                
            # Clean up temp file after delay
            self.window.after(10000, lambda: os.unlink(pdf_path))
                
        except Exception as e:
            messagebox.showerror("PDF Error", f"Failed to create PDF: {str(e)}")
    
    def append_text(self, text, style="normal", alignment="left", size=10, color=None, font_name="Arial"):
        # Create a unique tag name for this text style
        tag_name = f"{style}_{alignment}_{size}_{color}_{font_name}"
        
        # Configure the font
        if style == "bold":
            text_font = font.Font(family=font_name, size=size, weight="bold")
        else:
            text_font = font.Font(family=font_name, size=size)
        
        # Configure the tag with the font and alignment
        self.rich_text.tag_configure(tag_name, font=text_font)
        
        # Set alignment
        if alignment == "left":
            self.rich_text.tag_configure(tag_name, justify="left")
        elif alignment == "right":
            self.rich_text.tag_configure(tag_name, justify="right")
        elif alignment == "center":
            self.rich_text.tag_configure(tag_name, justify="center")
        
        # Set text color if specified
        if color:
            self.rich_text.tag_configure(tag_name, foreground=color)
        
        # Insert the text with the tag
        self.rich_text.insert(tk.END, text + "\n", tag_name)
    
    def generate_medical_certificate(self):
        # Clear previous content
        self.rich_text.delete(1.0, tk.END)
        
        # Get today's date
        today_date = datetime.now().strftime("%A, %d %B %Y")
        
        # Append the doctor's name in blue
        self.append_text("DR. BELINDA O. CABAUATAN", style="bold", alignment="left", size=18, color="blue")
        
        # Append specialization
        self.append_text("ADULT NEUROLOGY", style="bold", alignment="left", size=11)
        self.append_text("BRAIN, SPINAL CORD, NERVE AND MUSCLE SPECIALIST", style="bold", alignment="left", size=11)
        
        # Empty line
        self.rich_text.insert(tk.END, "\n")
        
        # Append the heading with Algerian font (using Arial as fallback if Algerian not available)
        self.append_text("               MEDICAL CERTIFICATE", style="bold", alignment="left", size=18, font_name="Algerian")
        
        # Empty line
        self.rich_text.insert(tk.END, "\n")
        
        # Patient information
        self.append_text(f"This is to certify that {self.patient_data['name']} {self.patient_data['age']} years old, from {self.patient_data['address']} was.", 
                        style="normal", alignment="left", size=10)
        self.append_text(f"seen and examined in this clinic on {today_date}.", 
                        style="normal", alignment="left", size=10)
        
        # Empty line
        self.rich_text.insert(tk.END, "\n")
        
        # Diagnosis
        self.append_text("DIAGNOSIS:", style="normal", alignment="left", size=12)
        self.append_text(self.patient_data.get('findings', ''), style="normal", alignment="left", size=10)
        
        # Add space
        for _ in range(4):  # Reduced space since we'll add remarks content
            self.rich_text.insert(tk.END, "\n")
        
        # Remarks section
        self.append_text("REMARKS:", style="normal", alignment="left", size=12)
        
        # Add remarks content if available
        if self.patient_data.get('remarks'):
            self.append_text(self.patient_data.get('remarks'), style="normal", alignment="left", size=10)
        else:
            # Add space if no remarks
            for _ in range(8):
                self.rich_text.insert(tk.END, "\n")
        
        # Add empty line
        self.rich_text.insert(tk.END, "\n")
        
        # Certification notice
        self.append_text("This certification is issued for reference use only.", 
                        style="normal", alignment="left", size=10)
        self.append_text(f"Issued this {today_date} at Iriga Clinic.", 
                        style="normal", alignment="left", size=10)
        
        # Add space
        for _ in range(8):
            self.rich_text.insert(tk.END, "\n")
        
        # Doctor info with right alignment
        self.append_text("DR. BELINDA O. CABAUATAN M.D.", style="normal", alignment="right", size=10)
        self.append_text("NEUROLOGY", style="normal", alignment="right", size=10)
        self.append_text("Lic. No.    109769", style="normal", alignment="right", size=10)
        self.append_text("PTR. No.    4813787", style="normal", alignment="right", size=10)
