from Bio import Entrez, SeqIO
import typer
import os
import pandas as pd


app = typer.Typer(add_completion=False)


def getOrganismNames(accession_numbers: list[str]) -> list[str]:
    # Use Entrez API to fetch organism names for accession numbers
    handle = Entrez.efetch(db='nucleotide', id=accession_numbers, rettype='gb', retmode='text')
    records = SeqIO.parse(handle, 'genbank')
    # Extract organism names from GenBank records
    return [record.annotations['organism'].strip() for record in records]


@app.command(no_args_is_help=True)
def main(
    input_file_path: str = typer.Argument(
        ...,
        help="Path to a CSV file with the Accession Numbers in the SECOND column.",
        show_default=False
    ),
    email: str = typer.Option(
        ...,
        prompt_required=True,
        help="Your email. Will be used to track your usage with NCBI so they can let you know before they block if you are using it too much."
    )
):
    print("Starting looker upper.")
    print(f"Looking up Accession Numbers from file: {input_file_path}")

    if not os.path.isfile(input_file_path):
        print(f"Couldn't find file: {input_file_path}.")
        return

    # with open(input_file_path, "r") as f:
    #     print(f"Getting Accession Numbers from file: {input_file_path}")
    #     accession_numbers = [line.strip() for line in f.readlines() if len(line.strip()) > 0 and not line.strip().startswith('#')]
    
    df = pd.read_csv(input_file_path, )
    column_2_values = df.iloc[:, 1].values
    accession_numbers = [accession_number.strip() for accession_number in column_2_values if len(accession_number.strip()) > 0]
    print(f"Found this many Accession Numbers: {len(accession_numbers)}")

    # # Set up email address for Entrez API
    Entrez.email = email
    
    organism_names = []
    for i in range(0, len(accession_numbers), 9900):
        print(f"Calling api with a max chunk size of 9900. Current index at: {i}")
        organism_names = organism_names + getOrganismNames(accession_numbers[i:i+9900])
        print(f"Got this many organism names on this trip: {len(organism_names)}")
        print(f"Total organism names collected so far: {len(organism_names)}")
        
    print(f"Got back this many organism names: {len(organism_names)}")
    df["taxonomy unmapped"] = pd.Series(organism_names)
    
    print(f"Writing values back into file: {input_file_path}")
    df.to_csv(input_file_path, index=False)





if __name__ == "__main__":
    app()



