"""Agent tool for arXiv paper search, download, and analysis."""

import os
from smolagents import CodeAgent, AgentLogger, LogLevel, tool
from smolagents.default_tools import FinalAnswerTool
from .llm_helper import create_openai_compatible_llm


# ============================================================================
# ARXIV TOOLS
# ============================================================================

@tool
def search_arxiv(query: str, max_results: int = 5, sort_by: str = "relevance") -> str:
    """
    Search arXiv for papers matching the query and return their metadata.

    Args:
        query: Search query string
        max_results: Maximum number of results to return (default: 5)
        sort_by: Sort criterion - "relevance" (default), "lastUpdatedDate", or "submittedDate"

    Returns:
        String containing paper metadata (title, authors, abstract, URL)
    """
    try:
        import arxiv

        sort_options = {
            "relevance": arxiv.SortCriterion.Relevance,
            "lastUpdatedDate": arxiv.SortCriterion.LastUpdatedDate,
            "submittedDate": arxiv.SortCriterion.SubmittedDate
        }
        sort_criterion = sort_options.get(sort_by, arxiv.SortCriterion.Relevance)

        client = arxiv.Client(page_size=100, delay_seconds=3.0, num_retries=3)
        search = arxiv.Search(query=query, max_results=max_results, sort_by=sort_criterion)
        results = list(client.results(search))

        if not results:
            return f"No papers found for query: '{query}'"

        result_text = f"Found {len(results)} papers matching query: '{query}'\n\n"

        for i, paper in enumerate(results, 1):
            result_text += f"Paper {i}:\n"
            result_text += f"Title: {paper.title}\n"
            result_text += f"Authors: {', '.join(author.name for author in paper.authors)}\n"
            result_text += f"Categories: {', '.join(paper.categories)}\n"
            result_text += f"Primary Category: {paper.primary_category}\n"
            result_text += f"Published: {paper.published}\n"
            result_text += f"Updated: {paper.updated}\n"
            result_text += f"DOI: {paper.doi if paper.doi else 'None'}\n"
            result_text += f"URL: {paper.entry_id}\n"
            result_text += f"PDF URL: {paper.pdf_url}\n"
            abstract = paper.summary.replace('\n', ' ')
            result_text += f"Abstract: {abstract}\n\n"

        return result_text

    except ImportError:
        return "Error: The 'arxiv' package is not installed. Please install it using 'pip install arxiv'."
    except Exception as e:
        return f"Error searching arXiv: {str(e)}"


@tool
def download_arxiv_paper(paper_id: str, output_dir: str = None) -> str:
    """
    Download a paper PDF from arXiv by its ID.

    Args:
        paper_id: The arXiv ID of the paper (e.g., "2103.12345" or the full URL)
        output_dir: Directory to save the PDF (defaults to ./arxiv_papers)

    Returns:
        Full absolute path to the downloaded PDF or error message
    """
    try:
        import arxiv
        import requests

        if output_dir is None:
            output_dir = "./arxiv_papers"

        os.makedirs(output_dir, exist_ok=True)

        if paper_id.startswith("http"):
            paper_id = paper_id.split("/")[-1]
            paper_id = paper_id.split("v")[0] if "v" in paper_id else paper_id

        search = arxiv.Search(id_list=[paper_id])
        results = list(search.results())
        if not results:
            raise ValueError(f"Could not find paper with ID '{paper_id}'")
        paper = results[0]

        filename = f"{paper_id}.pdf"
        filepath = os.path.join(output_dir, filename)

        # Workaround for arxiv package v2.3.0 bug where pdf_url is None
        pdf_url = f"https://arxiv.org/pdf/{paper_id}.pdf"
        response = requests.get(pdf_url)
        response.raise_for_status()
        with open(filepath, 'wb') as f:
            f.write(response.content)

        abs_filepath = os.path.abspath(filepath)
        return f"Successfully downloaded '{paper.title}' to {abs_filepath}"

    except ImportError:
        return "Error: The 'arxiv' package is not installed. Please install it using 'pip install arxiv'."
    except StopIteration:
        return f"Error: Could not find paper with ID '{paper_id}'"
    except Exception as e:
        return f"Error downloading paper: {str(e)}"


@tool
def download_full_arxiv_paper(paper_id: str, output_dir: str = None) -> str:
    """
    Download arXiv paper PDF and extract full text to TXT file for easier reading.

    Args:
        paper_id: The arXiv ID of the paper (e.g., "2103.12345" or the full URL)
        output_dir: Directory to save files (defaults to ./arxiv_papers)

    Returns:
        String with both PDF and TXT file paths, or error message
    """
    try:
        import arxiv
        import requests

        if output_dir is None:
            output_dir = "./arxiv_papers"

        os.makedirs(output_dir, exist_ok=True)

        if paper_id.startswith("http"):
            paper_id = paper_id.split("/")[-1]
            paper_id = paper_id.split("v")[0] if "v" in paper_id else paper_id

        search = arxiv.Search(id_list=[paper_id])
        results = list(search.results())
        if not results:
            raise ValueError(f"Could not find paper with ID '{paper_id}'")
        paper = results[0]

        pdf_filename = f"{paper_id}.pdf"
        pdf_filepath = os.path.join(output_dir, pdf_filename)

        # Workaround for arxiv package v2.3.0 bug where pdf_url is None
        pdf_url = f"https://arxiv.org/pdf/{paper_id}.pdf"
        response = requests.get(pdf_url)
        response.raise_for_status()
        with open(pdf_filepath, 'wb') as f:
            f.write(response.content)

        txt_filename = f"{paper_id}.txt"
        txt_filepath = os.path.join(output_dir, txt_filename)

        try:
            from pypdf import PdfReader
            reader = PdfReader(pdf_filepath)
            full_text = []

            for page_num, page in enumerate(reader.pages, 1):
                text = page.extract_text()
                full_text.append(f"--- Page {page_num} ---\n{text}\n")

            with open(txt_filepath, 'w', encoding='utf-8') as f:
                f.write(f"Title: {paper.title}\n")
                f.write(f"Authors: {', '.join(author.name for author in paper.authors)}\n")
                f.write(f"Published: {paper.published}\n")
                f.write(f"arXiv ID: {paper_id}\n")
                f.write(f"URL: {paper.entry_id}\n\n")
                f.write("=" * 80 + "\n")
                f.write("FULL TEXT\n")
                f.write("=" * 80 + "\n\n")
                f.write("\n".join(full_text))

        except ImportError:
            try:
                import pdfplumber
                full_text = []
                with pdfplumber.open(pdf_filepath) as pdf:
                    for page_num, page in enumerate(pdf.pages, 1):
                        text = page.extract_text()
                        full_text.append(f"--- Page {page_num} ---\n{text}\n")

                with open(txt_filepath, 'w', encoding='utf-8') as f:
                    f.write(f"Title: {paper.title}\n")
                    f.write(f"Authors: {', '.join(author.name for author in paper.authors)}\n")
                    f.write(f"Published: {paper.published}\n")
                    f.write(f"arXiv ID: {paper_id}\n")
                    f.write(f"URL: {paper.entry_id}\n\n")
                    f.write("=" * 80 + "\n")
                    f.write("FULL TEXT\n")
                    f.write("=" * 80 + "\n\n")
                    f.write("\n".join(full_text))

            except ImportError:
                raise ImportError("Neither 'pypdf' nor 'pdfplumber' is installed. Install one with 'pip install pypdf' or 'pip install pdfplumber'.")

        abs_pdf_path = os.path.abspath(pdf_filepath)
        abs_txt_path = os.path.abspath(txt_filepath)

        return f"Successfully downloaded and extracted '{paper.title}':\nPDF: {abs_pdf_path}\nTXT: {abs_txt_path}"

    except ImportError as e:
        raise ImportError(f"Missing required package: {str(e)}")
    except StopIteration:
        raise ValueError(f"Could not find paper with ID '{paper_id}'")
    except Exception as e:
        raise RuntimeError(f"Error downloading/extracting paper: {str(e)}")


@tool
def read_text_file(filepath: str) -> str:
    """
    Read and return the contents of a text file.

    Args:
        filepath: Path to the text file to read

    Returns:
        File contents as a string
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: File not found at {filepath}"
    except Exception as e:
        return f"Error reading file: {str(e)}"


@tool
def list_files(directory: str = ".") -> str:
    """
    List all files in a directory.

    Args:
        directory: Directory path to list (defaults to current directory)

    Returns:
        String listing all files in the directory
    """
    try:
        files = os.listdir(directory)
        if not files:
            return f"No files found in {directory}"
        return f"Files in {directory}:\n" + "\n".join(f"  - {f}" for f in sorted(files))
    except Exception as e:
        return f"Error listing files: {str(e)}"


ARXIV_AGENT_SYSTEM_PROMPT = """
You're a helpful agent named 'arxiv_agent'.

ARXIV AGENT WORKFLOW:

STEP 1 - SEARCH ARXIV:
    - Use search_arxiv to find 10 relevant papers matching the query
    - Review the abstracts returned by search_arxiv

STEP 2 - IDENTIFY RELEVANT PAPERS:
    - Analyze the abstracts to identify the 2-3 most relevant papers
    - Look for papers that directly address the methodology, equations, or techniques requested

STEP 3 - DOWNLOAD AND EXTRACT FULL PAPERS:
    - For each relevant paper identified:
      * Use download_full_arxiv_paper(paper_id) to download PDF and extract to TXT
      * This tool returns both PDF and TXT file paths
      * Read the TXT file to access the full paper text
    - Focus on methodology sections, equations, and specific boundaries/criteria

STEP 4 - EXTRACT RELEVANT INFORMATION:
    - Read the TXT files to find:
      * Specific equations or formulas
      * Classification boundaries or thresholds
      * Methodological details that answer the query
    - Take notes on what each paper contributes

STEP 5 - PROVIDE FINAL ANSWER:
    - Your final_answer must include:
      * Abstract summaries of relevant papers
      * Full absolute file paths to both PDF and TXT files
      * Extracted methods, equations, or boundaries found in the papers
      * Citations (author names, paper titles, arXiv IDs)

CRITICAL RULES:
    ⚠️  Check tools listed above BEFORE writing any code. If a tool exists for your task, USE IT.
    Only write custom code if no suitable tool exists or the existing tool is insufficient.

    - ALWAYS use download_full_arxiv_paper for papers you need to read in detail
    - ALWAYS include full absolute file paths in your final answer
    - If download_full_arxiv_paper throws an error, report it and try the next paper
    - Read the TXT files (not PDFs) to extract information
    - final_answer() must be in separate execution block AFTER all downloads complete

YOUR ROLE IS SIMPLE:
    1. Search arXiv for relevant papers
    2. Download and extract the most relevant ones
    3. Read them to find the specific information requested
    4. Return summaries, file paths, and extracted methods
"""

@tool
def arxiv_agent(
    query: str,
    api_key: str,
    llm_url: str,
    model_id: str,
    output_dir: str = "./arxiv_papers",
    max_steps: int = 15
) -> str:
    """
    Search, download, and analyze arXiv papers using an AI agent.

    This agent can search arXiv for papers, download PDFs, extract full text,
    and analyze papers to answer specific research questions.

    REQUIREMENTS:
    - Packages: arxiv, requests, pypdf or pdfplumber
      Install with: pip install arxiv requests pypdf

    Args:
        query: Research question or search task for the agent. Examples:
            - "What are the latest methods for galaxy mass estimation?"
            - "Find papers on dark matter detection and summarize the key techniques"
            - "Search for cosmological parameter estimation methods"
        api_key: API key for LLM service (required)
        llm_url: Base URL for LLM API endpoint (required)
            Example:
            - Google Gemini: "https://generativelanguage.googleapis.com/v1beta/openai/"
        model_id: Model identifier to use (required)
            Example:
            - Google: "gemini-2.0-flash-exp"
        output_dir: Directory to save downloaded papers (default: "./arxiv_papers")
        max_steps: Maximum agent steps (default: 15)

    Returns:
        str: Agent's analysis including:
            - Paper summaries
            - File paths to downloaded PDFs and TXT files
            - Extracted information answering the query

    Example:
        result = run_arxiv_agent(
            query="What are the latest methods for galaxy mass estimation?",
            api_key="your-api-key",
            llm_url="https://api.anthropic.com",
            model_id="claude-3-5-sonnet-20241022"
        )
    """
    try:
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        original_dir = os.getcwd()
        os.chdir(output_dir)

        # Create the LLM model
        try:
            model = create_openai_compatible_llm(api_key, llm_url, model_id)
        except ValueError as e:
            os.chdir(original_dir)
            return f"LLM Configuration Error: {str(e)}"
        except ImportError as e:
            os.chdir(original_dir)
            return f"Installation Error: {str(e)}"

        # Create agent with arXiv tools
        tools = [
            search_arxiv,
            download_arxiv_paper,
            download_full_arxiv_paper,
            read_text_file,
            list_files,
            FinalAnswerTool()
        ]

        agent = CodeAgent(
            model=model,
            tools=tools,
            max_steps=max_steps,
            verbosity_level=1,
            logger=AgentLogger(level=LogLevel.INFO),
            name="arxiv_agent",
            description="Searches arXiv, downloads papers, and performs semantic analysis.",
            additional_authorized_imports=["arxiv", "requests", "pypdf", "pdfplumber"]
        )

        # Run the agent
        result = agent.run(ARXIV_AGENT_SYSTEM_PROMPT + "\n" + query)

        # Return to original directory
        os.chdir(original_dir)

        return str(result)

    except Exception as e:
        # Make sure we return to original directory even on error
        try:
            os.chdir(original_dir)
        except:
            pass
        import traceback
        return f"Error running arXiv agent: {str(e)}\n{traceback.format_exc()}"