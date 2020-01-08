const getReadabilityIndex = text => {
    /* eslint-disable */
    // Constants for our reading level calculation
    // These are part of the Automated Readability Index calculation
    // https://en.wikipedia.org/wiki/Automated_readability_index
    var CHARACTER_WEIGHT = 4.71;
    var SENTENCE_WEIGHT = 0.5;
    var BASE = 21.43;

    // Create the variables to hold the character, word and sentence counts
    var charCount = 0;
    var wordCount = 0;
    var sentenceCount = 0;

    var textClean = text.replace(/[^a-zA-Z ]/g, "");

    // Calculate the character count
    var textNoSpace = textClean.replace(/\s/g, "");
    var textNoPeriod = textNoSpace.replace(/\./g, "");
    charCount = textNoPeriod.length;

    // Calculate the word count -----------------
    var wordArray = textClean.split(" ");
    var wordArrayNoSpaces = wordArray.filter(v => v != "");
    wordCount = wordArrayNoSpaces.length;

    // Calculate the sentence count
    sentenceCount = text.replace(/\S[.?!](\s|$)/g, "$1|").split("|").length - 1;

    // If we have an empty first value in the array we know our text box is actually empty
    // so we need to minus 1 from our word count
    if (text.split(" ")[0] == "") {
        wordCount -= 1;
    }

    var readabilityScore =
        CHARACTER_WEIGHT * (charCount / wordCount) +
        SENTENCE_WEIGHT * (wordCount / sentenceCount) -
        BASE;

    var readingAge = (readabilityScore + 4).toFixed(0);
    // Modify the help area to include the new information
    if (isFinite(readingAge)) {
        if (readingAge > 18) {
            readingAge = "18+";
        } else if (readingAge < 4) {
            readingAge = 4;
        }
        return {
            age: readingAge,
            score: readabilityScore,
            words: wordCount,
            sentences: sentenceCount
        };
    } else {
        return null;
    }
};

const { ToolbarButton } = window.Draftail;
const React = window.React;

const Readability = ({ getEditorState }) => {
    const editorState = getEditorState();
    const content = editorState.getCurrentContent();
    const text = content.getPlainText();
    const stats = getReadabilityIndex(text);
    const label = `Reading age: ${stats ? stats.age : "?"}`;
    return React.createElement(ToolbarButton, {
        name: 'READABILITY',
        label,
    });
};

window.draftail.registerControl(Readability);
