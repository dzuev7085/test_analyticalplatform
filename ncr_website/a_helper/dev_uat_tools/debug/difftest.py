import diff_match_patch

textA = "We believe that the credit profile will improve significantly in the near term. This is driven by a underlying factors such as a, b and c."
textB = "We believe that the credit profile will improve in the near term. This is mainly driven by a underlying factors such as a, b and c."

#create a diff_match_patch object
dmp = diff_match_patch.diff_match_patch()

# Depending on the kind of text you work with, in term of overall length
# and complexity, you may want to extend (or here suppress) the
# time_out feature
dmp.Diff_Timeout = 0   # or some other value, default is 1.0 seconds

# All 'diff' jobs start with invoking diff_main()
diffs = dmp.diff_main(textA, textB)

# diff_cleanupSemantic() is used to make the diffs array more "human" readable
dmp.diff_cleanupSemantic(diffs)

# and if you want the results as some ready to display HMTL snippet
htmlSnippet = dmp.diff_prettyHtml(diffs)

print(htmlSnippet)
