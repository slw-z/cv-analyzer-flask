# ============================================================================
# FLASK CV ANALYZER PRO - APPLICATION COMPLÈTE
# ============================================================================

from flask import Flask, render_template, request, redirect, url_for, flash
import os
from werkzeug.utils import secure_filename
import re
from collections import Counter
from pathlib import Path

# --- IMPORTS CORRIGÉS ---
import PyPDF2
import docx
# ------------------------

app = Flask(__name__)
app.secret_key = 'votre_secret_key_ici_change_moi'  # Nécessaire pour flash messages

# Configuration
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}

# Créer le dossier uploads
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


# ============================================================================
# CLASSE CV ANALYZER PRO (Version Flask adaptée)
# ============================================================================

class CVAnalyzerPro:
    """Analyseur CV adapté pour Flask"""
    
    def __init__(self):
        self.stop_words = {
            'le', 'la', 'les', 'un', 'une', 'des', 'de', 'du', 'et', 'à', 
            'dans', 'pour', 'par', 'avec', 'sur', 'ce', 'qui', 'il', 'elle',
            'au', 'aux', 'ou', 'mais', 'donc', 'or', 'ni', 'car', 'en', 'je',
            'tu', 'nous', 'vous', 'ils', 'elles', 'son', 'sa', 'ses', 'leur',
            'leurs', 'mon', 'ma', 'mes', 'ton', 'ta', 'tes', 'notre', 'votre',
            'est', 'sont', 'être', 'avoir', 'fait', 'faire', 'peut', 'tout'
        }
        
        self.tech_skills = {
            'python', 'java', 'javascript', 'sql', 'aws', 'azure', 'gcp',
            'docker', 'kubernetes', 'react', 'angular', 'vue', 'node',
            'mongodb', 'postgresql', 'mysql', 'pandas', 'numpy', 'scikit',
            'tensorflow', 'pytorch', 'spark', 'hadoop', 'kafka', 'git',
            'jenkins', 'ci/cd', 'agile', 'scrum', 'excel', 'powerbi',
            'tableau', 'sagemaker', 'lambda', 'ec2', 's3', 'api', 'rest',
            'graphql', 'machine learning', 'deep learning', 'nlp', 'data',
            'analytics', 'etl', 'cloud', 'linux', 'windows', 'bash',
            'power bi', 'power query', 'dax', 'vba', 'r', 'sas', 'spss',
            'fabric', 'lakehouse', 'dataverse', 'statistiques', 'statistics',
            'flutter', 'dart', 'flask'
        }
    
    def clean_and_tokenize(self, text):
        """Nettoie et découpe le texte"""
        text = text.lower()
        text = re.sub(r'[^a-zàâäçéèêëîïôùûüÿ0-9\s+#-]', ' ', text)
        words = text.split()
        keywords = [
            word for word in words 
            if word not in self.stop_words and len(word) > 2
        ]
        return keywords
    
    def extract_technical_skills(self, text):
        """Extrait les compétences techniques"""
        text_lower = text.lower()
        found_skills = [skill for skill in self.tech_skills if skill in text_lower]
        return set(found_skills)
    
    def calculate_match_score(self, cv_keywords, job_keywords):
        """Calcule le score de compatibilité"""
        cv_set = set(cv_keywords)
        job_set = set(job_keywords)
        
        if not job_set:
            return 0
        
        common = cv_set.intersection(job_set)
        score = (len(common) / len(job_set)) * 100
        return round(score, 2)
    
    def interpret_score(self, score, is_junior=True):
        """Interprète le score"""
        if is_junior:
            if score < 8:
                return {
                    'status': 'incompatible',
                    'emoji': '❌',
                    'title': 'PROFIL INCOMPATIBLE',
                    'message': 'Ce poste ne correspond pas à votre profil.',
                    'color': 'danger'
                }
            elif score < 12:
                return {
                    'status': 'distant',
                    'emoji': '⚠️',
                    'title': 'PROFIL ÉLOIGNÉ',
                    'message': 'Adaptez fortement votre CV.',
                    'color': 'warning'
                }
            elif score < 18:
                return {
                    'status': 'acceptable',
                    'emoji': '✅',
                    'title': 'PROFIL JUNIOR ACCEPTABLE',
                    'message': 'Score NORMAL pour un junior. Adaptez 2-3 éléments et POSTULEZ !',
                    'color': 'success'
                }
            elif score < 25:
                return {
                    'status': 'good',
                    'emoji': '✅✅',
                    'title': 'BON MATCH',
                    'message': 'Très bon score ! Postulez avec confiance.',
                    'color': 'success'
                }
            else:
                return {
                    'status': 'excellent',
                    'emoji': '🎯',
                    'title': 'EXCELLENT MATCH',
                    'message': 'Match exceptionnel ! Postulez en priorité !',
                    'color': 'success'
                }
        return None
    
    def analyze(self, cv_text, job_text, is_junior=True):
        """Analyse complète - retourne un dictionnaire de résultats"""
        
        # Tokenization
        cv_keywords = self.clean_and_tokenize(cv_text)
        job_keywords = self.clean_and_tokenize(job_text)
        
        # Extraction compétences
        cv_skills = self.extract_technical_skills(cv_text)
        job_skills = self.extract_technical_skills(job_text)
        
        # Calculs
        score = self.calculate_match_score(cv_keywords, job_keywords)
        missing_keywords = set(job_keywords) - set(cv_keywords)
        missing_skills = job_skills - cv_skills
        common_skills = cv_skills.intersection(job_skills)
        
        # Interprétation
        interpretation = self.interpret_score(score, is_junior)
        
        # Top mots-clés
        job_counter = Counter(job_keywords)
        top_keywords = job_counter.most_common(15)
        
        # Keywords avec statut
        keywords_with_status = [
            {
                'word': word,
                'count': count,
                'in_cv': word in cv_keywords
            }
            for word, count in top_keywords
        ]
        
        # Suggestions de compétences manquantes
        skill_suggestions = []
        for skill in list(missing_skills)[:7]:
            priority = 'CRITIQUE' if skill in ['sql', 'python', 'excel', 'power bi'] else 'IMPORTANT'
            skill_suggestions.append({
                'skill': skill,
                'priority': priority
            })
        
        # Suggestions de mots-clés
        keyword_suggestions = [
            {
                'keyword': word,
                'frequency': count
            }
            for word, count in job_counter.most_common(20)
            if word in missing_keywords and count >= 2 and len(word) > 4
        ][:7]
        
        # Estimation d'amélioration
        potential_improvement = len(skill_suggestions) * 2 + len(keyword_suggestions) * 1
        estimated_new_score = min(round(score + potential_improvement, 1), 30)
        
        return {
            'score': score,
            'interpretation': interpretation,
            'stats': {
                'cv_keywords': len(set(cv_keywords)),
                'job_keywords': len(set(job_keywords)),
                'common_keywords': len(set(cv_keywords) & set(job_keywords)),
                'cv_skills': len(cv_skills),
                'job_skills': len(job_skills),
                'common_skills': len(common_skills)
            },
            'skills': {
                'common': sorted(list(common_skills)),
                'missing': sorted(list(missing_skills))
            },
            'top_keywords': keywords_with_status,
            'suggestions': {
                'skills': skill_suggestions,
                'keywords': keyword_suggestions
            },
            'improvement': {
                'current': score,
                'estimated': estimated_new_score,
                'gain': round(estimated_new_score - score, 1)
            }
        }


# ============================================================================
# FONCTIONS UTILITAIRES
# ============================================================================

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(pdf_path):
    """Extrait le texte d'un PDF"""
    try:
        text = ""
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text
    except Exception as e:
        return f"Erreur PDF: {str(e)}"

def extract_text_from_docx(docx_path):
    """Extrait le texte d'un Word"""
    try:
        doc = docx.Document(docx_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text
    except Exception as e:
        return f"Erreur DOCX: {str(e)}"

def extract_text_from_file(file_path):
    """Détecte le type et extrait le texte"""
    file_path = Path(file_path)
    suffix = file_path.suffix.lower()
    
    if suffix == '.pdf':
        return extract_text_from_pdf(file_path)
    elif suffix in ['.docx', '.doc']:
        return extract_text_from_docx(file_path)
    elif suffix == '.txt':
        return file_path.read_text(encoding='utf-8')
    else:
        return "Format non supporté"


# ============================================================================
# ROUTES FLASK
# ============================================================================

@app.route('/')
def home():
    """Page d'accueil"""
    return render_template('index.html')

@app.route('/analyser', methods=['POST'])
def analyser():
    """Route d'analyse"""
    
    # Vérifier le fichier CV
    if 'cv' not in request.files:
        flash('Aucun fichier CV uploadé', 'error')
        return redirect(url_for('home'))
    
    file = request.files['cv']
    
    if file.filename == '':
        flash('Aucun fichier sélectionné', 'error')
        return redirect(url_for('home'))
    
    if not allowed_file(file.filename):
        flash('Type de fichier non autorisé. Utilisez PDF, DOCX ou TXT', 'error')
        return redirect(url_for('home'))
    
    # Sauvegarder le fichier
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    # Extraire le texte du CV
    cv_text = extract_text_from_file(filepath)
    
    if not cv_text or len(cv_text) < 50:
        flash('Impossible d\'extraire le texte du CV ou CV trop court', 'error')
        return redirect(url_for('home'))
    
    # Récupérer l'offre d'emploi
    job_offer_text = request.form.get('offre', '')
    
    if not job_offer_text or len(job_offer_text) < 50:
        flash('Offre d\'emploi manquante ou trop courte', 'error')
        return redirect(url_for('home'))
    
    # Analyser avec CVAnalyzerPro
    analyzer = CVAnalyzerPro()
    results = analyzer.analyze(cv_text, job_offer_text, is_junior=True)
    
    # Supprimer le fichier uploadé (optionnel, pour économiser l'espace)
    try:
        os.remove(filepath)
    except:
        pass
    
    # Afficher les résultats
    return render_template('results.html', results=results, cv_filename=filename)

@app.route('/about')
def about():
    """Page à propos"""
    return render_template('about.html')


# ============================================================================
# LANCEMENT DE L'APPLICATION
# ============================================================================

if __name__ == '__main__':
    app.run(debug=True, port=5000)