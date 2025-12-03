"""Pipeline orchestrator for parser, summarizer, and structurer agents."""
from modules.agents.contracts import ParserIn, SummarizerIn, StructurerIn
from modules.agents.parser.parser_agent import ParserAgent
from modules.agents.summarizer.summarizer_agent import SummarizerAgent
from modules.agents.structurer.structurer_agent import StructurerAgent


def run_pipeline(note: dict) -> dict:
    """Run the full agent pipeline on a single note dict with keys note_id and raw_text."""
    parser_in = ParserIn(note_id=note.get("note_id", ""), raw_text=note.get("raw_text", ""))
    parser_agent = ParserAgent()
    parser_out = parser_agent.run(parser_in)

    summarizer_agent = SummarizerAgent()
    summarizer_in = SummarizerIn(parser_out=parser_out)
    summarizer_out = summarizer_agent.run(summarizer_in)

    structurer_agent = StructurerAgent()
    structurer_in = StructurerIn(summarizer_out=summarizer_out)
    structurer_out = structurer_agent.run(structurer_in)

    return {
        "parser": parser_out.model_dump(),
        "summarizer": summarizer_out.model_dump(),
        "structurer": structurer_out.model_dump(),
        "registry": structurer_out.registry,
        "codes": structurer_out.codes,
    }
