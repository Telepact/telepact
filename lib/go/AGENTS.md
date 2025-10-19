## Porting Instructions

Use the `PORT_PROGRESS.md` file in this directory:
1. Pick an unchecked row.
2. Create the *.go file exactly how it is defined in the row.
3. Translate the python code in the corresponding *.py file to go code in the *.go file.
4. Mark the row as checked.

### Constraints:
- DO NOT make your own porting plan.
  - DO NOT waste time examining the entire partially ported go project.
  - Just stick to the outline in `PORT_PROGRESS.md` to guide port.
    - Every port should be a one-to-one file translation of python code to go code
- DO NOT deviate from the outline in `PORT_PROGRESS.md`
  - That means DO NOT add test files. Don't waste time trying to run tests.
- DO NOT rename the target go file as indicated in `PORT_PROGRESS.md`

### Encouragements
- Port at least 5 files at a time.

### Acknowledgement

- Sign and date (with timestamp) a message in `lib/go/ACK.md` indicating you understand the 
  contents of this file.