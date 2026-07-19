cd ~/claude_projects/spring-break/cheat-sheets
java -jar ~/claude_projects/pagewright/pagewright-cli/target/pagewright-cli-0.1.0-SNAPSHOT-all.jar \
  build -s A5  \
  --report-pages  --theme console-first --theme-dir themes cards ../spring-break-cheat-sheets.pdf
