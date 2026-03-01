# Reporter Fine-Tuning Pipeline

Fine-tune GPT-4o-mini (or GPT-4o) on 10,600 IP operative report examples to
create a model that transforms procedure dictations → synoptic reports.

## Quick Start

```bash
# 1. Set your API key
export OPENAI_API_KEY=sk-...

# 2. Prep is already done — the fine_tuning/ directory has ready-to-upload files.
#    If you want to regenerate from source:
#    python prepare_finetune.py --input /path/to/reporter_training/reporter_training

# 3. Upload files and launch fine-tuning
python launch_finetune.py
#   → Creates the job, prints a job ID
#   → GPT-4o-mini: ~$10 for 3 epochs, finishes in 2-4 hours

# 4. Check status
python launch_finetune.py --status --job-id ftjob-XXXXXX
#   Or wait for completion:
python launch_finetune.py --status --job-id ftjob-XXXXXX --wait

# 5. Evaluate
python eval_finetune.py --model ft:gpt-4o-mini-2024-07-18:your-org::jobid
#   → Runs 2,120 validation cases
#   → Reports section coverage, text similarity, clinical detail recall
#   → Breaks down scores by input style and procedure type

# 6. Evaluate specific slices
python eval_finetune.py --model ft:... --style sloppy --max-cases 100
python eval_finetune.py --model ft:... --procedure stent
python eval_finetune.py --model ft:... --save-outputs  # save full generated text
```

## Files

| File | Purpose |
|------|---------|
| `prepare_finetune.py` | Converts reporter_training JSONL → OpenAI chat format |
| `launch_finetune.py` | Uploads files, starts job, monitors status |
| `eval_finetune.py` | Evaluates fine-tuned model with style/procedure breakdowns |
| `fine_tuning/reporter_ft_train.jsonl` | 8,480 training examples (ready to upload) |
| `fine_tuning/reporter_ft_valid.jsonl` | 2,120 validation examples (ready to upload) |
| `fine_tuning/reporter_ft_manifest.json` | Token stats and cost estimates |

## Dataset Stats

- **8,480 train** / **2,120 validation** examples
- **106 unique clinical scenarios** (stents, EBUS, cryo, robotic bronch, etc.)
- **5 input styles** per scenario (structured, narrative, sloppy, billing, formatted)
- **Avg ~1,287 tokens** per example (prompt + system + completion)
- **No examples exceed 8K tokens** — well within fine-tuning limits

## Cost Estimates

| Model | 2 Epochs | 3 Epochs | 4 Epochs |
|-------|----------|----------|----------|
| GPT-4o-mini | $6.55 | $9.83 | $13.10 |
| GPT-4o | $65.52 | $98.28 | $131.04 |

**Recommendation:** Start with GPT-4o-mini at 3 epochs (~$10). Only move to GPT-4o
if mini doesn't pass quality gates.

## Evaluation Metrics

The eval script measures:

- **Section Coverage**: Are all 9 required report sections present? (gate: ≥ 0.99)
- **Text Similarity**: SequenceMatcher ratio vs gold reports (how close to your style)
- **Clinical Detail Recall**: Do device sizes, station numbers, measurements survive? 
- **Length Ratio**: Is the output roughly the right length? (ideal: ~1.0)

Results are broken down by **input style** (to catch sloppy-input degradation) and
**procedure type** (to catch per-procedure failures).

## Customizing the System Prompt

The default system prompt is embedded in every training example. To change it:

```bash
# Write your custom prompt to a file
echo "Your custom system prompt here..." > my_system_prompt.txt

# Regenerate with custom prompt (re-run from source data)
python prepare_finetune.py \
  --input /path/to/reporter_training/reporter_training \
  --system-prompt my_system_prompt.txt
```

## Using GPT-4o Instead

```bash
python launch_finetune.py --model gpt-4o-2024-08-06 --suffix reporter-v1-4o --epochs 2
```

## After Fine-Tuning: Integration with Procedure Suite

Once you have a fine-tuned model that passes gates, integrate it as a new
reporter strategy:

```python
# In app/reporting/config.py, add:
REPORTER_SEED_STRATEGY = "fine_tuned"  # new option

# In app/reporting/fine_tuned_strategy.py:
from openai import OpenAI

def generate_report(note_text: str) -> str:
    client = OpenAI()
    response = client.chat.completions.create(
        model="ft:gpt-4o-mini-2024-07-18:your-org::jobid",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": note_text},
        ],
        max_tokens=4096,
        temperature=0.2,
    )
    return response.choices[0].message.content
```

## Iterating if Results Aren't Good Enough

1. **Check per-style scores** — if sloppy inputs fail, upsample sloppy examples
2. **Check per-procedure scores** — weak procedures need more training scenarios
3. **Check missing sections** — if CONSENT is often missing, verify training data
4. **Try more epochs** (4 instead of 3) or **GPT-4o** as the base model
5. **Augment training data** — add generator scripts for underrepresented procedures
   (IPC, pleuroscopy, thoracentesis, foreign body removal)
