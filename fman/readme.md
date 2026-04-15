# feynman
"AI research agent - Reads papers, searches the web, writes drafts, runs experiments, and cites every claim"

* ref: https://www.feynman.is/
* https://www.feynman.is/docs/getting-started/quickstart

## post install

```
> feynman setup

  Model: anthropic/claude-opus-4-6
✓ pandoc already installed at /usr/bin/pandoc

◆ Ready
  Model: anthropic/claude-opus-4-6
  alphaXiv: configured
  Preview: configured
  Web: Auto


> feynman
    /deepresearch What ar.....
```


## help

```
 Feynman Help                                                                                                                                                                    

 → --- Research Workflows ---                                                                                                                                                    
   /audit <item> — Compare a paper's claims against its public codebase and identify mismatches, omissions, and reproducibility risks.                                           
   /autoresearch <idea> — Autonomous experiment loop — try ideas, measure results, keep what works, discard what doesn't, repeat.                                                
   /compare <topic> — Compare multiple sources on a topic and produce a source-grounded matrix of agreements, disagreements, and confidence.                                     
   /deepresearch <topic> — Run a thorough, source-heavy investigation on a topic and produce a durable research brief with inline citations.                                     
   /draft <topic> — Turn research findings into a polished paper-style draft with equations, sections, and explicit claims.                                                      
   /lit <topic> — Run a literature review on a topic using paper search and primary-source synthesis.                                                                            
   /replicate <paper> — Plan or execute a replication workflow for a paper, claim, or benchmark.                                                                                 
   /review <artifact> — Simulate an AI research peer review with likely objections, severity, and a concrete revision plan.                                                      
   /watch <topic> — Set up a recurring or deferred research watch on a topic, company, paper area, or product surface.                                                           
   --- Project & Session ---                                                                                                                                                     
   /jobs — Inspect active background research work, including running processes and scheduled follow-ups.                                                                        
   /log — Write a durable session log with completed work, findings, open questions, and next steps.                                                                             
   /help — Show grouped Feynman commands and prefill the editor with a selected command.                                                                                         
   /init — Bootstrap AGENTS.md and session-log folders for a research project.                                                                                                   
   /outputs — Browse all research artifacts (papers, outputs, experiments, notes).                                                                                               
   --- Agents & Delegation ---                                                                                                                                                   
   /agents — Open the Agents Manager                                                                                                                                             
   /run <agent> <task> — Run a subagent directly: /run agent[output=file] task [--bg] [--fork]                                                                                   
   /chain agent1 -> agent2 — Run agents in sequence: /chain scout "task" -> planner [--bg] [--fork]                                                                              
   /parallel agent1 -> agent2 — Run agents in parallel: /parallel scout "task1" -> reviewer "task2" [--bg] [--fork]                                                              
   --- Bundled Package Commands ---                                                                                                                                              
   /ps — View and manage background processes                                                                                                                                    
   /schedule-prompt — Manage scheduled prompts interactively                                                                                                                     
   /preview — Rendered markdown preview (--pick select response, --file <path> or bare path, --browser for HTML, --pdf for PDF, --terminal to force inline)         

```