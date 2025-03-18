import streamlit as st
from Bio import SeqIO
import io

def validate_sequence(sequence):
    """Check if the sequence is exactly 150 bases and contains only A, T, G, C."""
    sequence = sequence.strip().upper()
    if len(sequence) != 150:
        return "The sequence must be exactly 150 bases long."
    elif any(base not in "ATGC" for base in sequence):
        return "The sequence must only contain A, T, G, or C."
    return None

def extract_fasta_sequence(fasta_file):
    """Extracts sequences from a FASTA file and ensures they meet the criteria."""
    try:
        fasta_content = fasta_file.read().decode("utf-8")
        fasta_io = io.StringIO(fasta_content)
        sequences = [str(record.seq).strip().upper() for record in SeqIO.parse(fasta_io, "fasta")]
        
        if not sequences:
            return None, "The FASTA file does not contain any valid sequences."
        
        errors = [validate_sequence(seq) for seq in sequences]
        if any(errors):
            return None, errors[0]  # Return first encountered error
        
        return sequences[0], None  # Return valid sequences
    except Exception as e:
        return None, f"Error processing FASTA file: {e}"

def show_upload():
    st.title("Upload Sequence for Promoter Prediction")
    
    st.write("""
        ## Instructions
        - Submit either a **nucleotide sequence** (150 bases) or a **FASTA file**.
        - The sequence should be in **A, T, G, C** format (no special characters).
        - If uploading a FASTA file, ensure all sequences are exactly **150 bases** long.
        - Select the **organism** the sequence belongs to.
    """)
    
    input_option = st.radio("Choose input method:", ("Submit Sequence", "Upload FASTA File"), key="input_method")
    
    if "sequence" not in st.session_state:
        st.session_state.sequence = None
    if "organism" not in st.session_state:
        st.session_state.organism = None
    sequence = ""
    fasta_file = None
    fasta_error = None

    if input_option == "Submit Sequence":
        sequence = st.text_area("Enter your 150-length nucleotide sequence:", height=150, key="sequence_input")
    else:
        fasta_file = st.file_uploader("Upload FASTA File:", type=["fasta", "fa", "txt"], key="fasta_upload")
        if fasta_file:
            sequence, fasta_error = extract_fasta_sequence(fasta_file)

    organisms = [
        "Haloferax_volcanii_DS2", "Helicobacter pylori 26695", "Klebsiella pneumoniae subsp. pneumoniae MGH 78578",
        "Mycobacterium tuberculosis H37Rv", "Nostoc sp. PCC 7120 = FACHB-418", "Pseudomonas aeruginosa UCBPP-PA14",
        "Saccharolobus solfataricus P2", "Salmonella enterica subsp. enterica serovar Typhimurium str. SL1344", "Streptomyces coelicolor A3(2)",
        "Synechocystis sp. PCC 6803", "Thermococcus kodakarensis KOD1", "Bacillus amyloliquefaciens XH7",
        "Chlamydia pneumoniae CWL029", "Corynebacterium glutamicum ATCC 13032", "Escherichia coli str. K-12 substr. MG1655"
    ]
    
    selected_organism = st.selectbox("Select the organism:", ["Select an organism"] + organisms, key="organism_selection")
    
    if st.button("Submit", key="submit_button"):
        errors = []
        
        if selected_organism == "Select an organism":
            errors.append("Please select an organism.")
        
        if input_option == "Submit Sequence":
            sequence_error = validate_sequence(sequence)
            if sequence_error:
                errors.append(sequence_error)
        else:
            if fasta_file is None:
                errors.append("Please upload a FASTA file.")
            elif fasta_error:
                errors.append(fasta_error)

        if errors:
            for error in errors:
                st.warning(error)
        else:
            st.session_state.sequence = sequence
            st.session_state.organism = selected_organism
            st.success("Sequence submitted successfully! Please go to the results page to see the results.")

if __name__ == "__main__":
    show_upload()
