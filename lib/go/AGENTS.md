## Porting Instructions

Use the `PORT_PROGRESS.md` file in this directory:
1. Pick an unchecked row.
2. Create the *.go file exactly how it is defined in the row.
3. Translate the python code in the corresponding *.py file to go code in the *.go file.
4. Mark the row as checked.

I repeat, DO NOT make your own porting plan. Every port should be a one-to-one
file translation of python code to go code, so just use the outline in
`PORT_PROGRESS.md` to help with that process. DO NOT deviate from the
outline in `PORT_PROGRESS.md`; DO NOT add test files.