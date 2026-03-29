# oh-my-claudecode

* https://github.com/yeachan-heo/oh-my-claudecode

## install

```

/plugin marketplace add https://github.com/Yeachan-Heo/oh-my-claudecode
/plugin install oh-my-claudecode
/reload-plugins

    ! gh auth login
    /setup


/omc-setup

● User answered Claude's questions:                                                                                                                                                                               
  ⎿  · Where should I configure oh-my-claudecode? → Global (all projects)    


Which parallel execution mode should be your default when you say 'fast' or 'parallel'?                                                                                             
                                                                                                                                                                                      
❯ 1. ultrawork (maximum capability)                                                                                                                                                   
     Uses all agent tiers including Opus for complex tasks. Best for challenging work where quality matters most. (Recommended)                                                       
  2. Skip / decide later                                                                                                                                                              
     Don't set a default now. You can always use explicit keywords like 'ulw' for ultrawork.                                                                                        
  3. Type something. 


```

```
● ---                                                                                                                                                                              
  OMC Setup Complete!                                                                                                                                                                 
                                               
  You don't need to learn any commands. I now have intelligent behaviors that activate automatically.                                                                                 
                                                                                                                                                                                      
  WHAT HAPPENS AUTOMATICALLY:                                                                                                                                                         
  - Complex tasks → I parallelize and delegate to specialists                                                                                                                         
  - "plan this" → I start a planning interview                                                                                                                                        
  - "don't stop until done" → I persist until verified complete                                                                                                                    
  - "stop" or "cancel" → I intelligently stop current operation                                                                                                                       
                                                                                                                                                                                      
  MAGIC KEYWORDS (optional power-user shortcuts):                                                                                                                                     
                                                                                                                                                                                      
  ┌─────────┬────────────────────┬─────────────────────────────┐                                                                                                                      
  │ Keyword │       Effect       │           Example           │                                                                                                                      
  ├─────────┼────────────────────┼─────────────────────────────┤                                                                                                                   
  │ ralph   │ Persistence mode   │ "ralph: fix the auth bug"   │
  ├─────────┼────────────────────┼─────────────────────────────┤
  │ ralplan │ Iterative planning │ "ralplan this feature"      │                                                                                                                      
  ├─────────┼────────────────────┼─────────────────────────────┤                                                                                                                      
  │ ulw     │ Max parallelism    │ "ulw refactor the API"      │                                                                                                                      
  ├─────────┼────────────────────┼─────────────────────────────┤                                                                                                                      
  │ plan    │ Planning interview │ "plan the new endpoints"    │                                                                                                                   
  ├─────────┼────────────────────┼─────────────────────────────┤                                                                                                                      
  │ team    │ Coordinated agents │ /team 3:executor fix errors │                                                                                                                   
  └─────────┴────────────────────┴─────────────────────────────┘                                                                                                                      
                                               
  ralph includes ultrawork: When you activate ralph mode, it automatically includes ultrawork's parallel execution.                                                                   
                                                                                                                                                                                   
  TEAMS:                                                                                                                                                                              
  - /oh-my-claudecode:team 3:executor "fix all TypeScript errors"                                                                                                                  
  - /oh-my-claudecode:team 5:debugger "fix build errors in src/"                                                                                                                      
                                                                
  HUD STATUSLINE: The status bar now shows OMC state. Restart Claude Code to see it.                                                                                                  
                                                                                                                                                                                      
  OMC CLI HELPERS:                                                                                                                                                                    
  - omc hud — Render the current HUD statusline                                                                                                                                       
  - omc teleport — Create an isolated git worktree                                                                                                                                    
  - omc team status — Inspect a running team job  
                                                                                                                                                                                      
  ---                                                                                                                                                                                 
  If you enjoy oh-my-claudecode, consider starring the repo:
  https://github.com/Yeachan-Heo/oh-my-claudecode                                                                                                                                     
                                                                                                                                                                                   
  That's it — just use Claude Code normally!                                                                                                                                          
                                                                                                                                                                                      
✻ Crunched for 3m 16s                                  
```