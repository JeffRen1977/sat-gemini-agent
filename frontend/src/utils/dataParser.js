// frontend/src/utils/dataParser.js

export const parseQuestionText = (questionText) => {
  const parsed = {};
  let remainingText = questionText; // Work with a mutable copy of the text

  // 1. Parse and remove Passage (if exists)
  const passageMatch = remainingText.match(/---BEGIN PASSAGE---\s*([\s\S]*?)\s*---END PASSAGE---/);
  if (passageMatch && passageMatch[1]) {
    parsed.passage = passageMatch[1].trim();
    remainingText = remainingText.replace(passageMatch[0], '').trim(); // Remove the passage block
  } else {
    parsed.passage = null;
  }

  // 2. Parse and remove Explanation (usually at the very end)
  const explanationMatch = remainingText.match(/Explanation:\s*([\s\S]*)/);
  if (explanationMatch && explanationMatch[1]) {
    parsed.explanation = explanationMatch[1].trim();
    remainingText = remainingText.replace(explanationMatch[0], '').trim(); // Remove explanation
  } else {
    parsed.explanation = 'No detailed explanation provided by the AI.';
  }

  // 3. Parse and remove Correct Answer (usually right before explanation)
  const correctAnswerMatch = remainingText.match(/Correct Answer:\s*(.*)/);
  if (correctAnswerMatch && correctAnswerMatch[1]) {
    parsed.correctAnswer = correctAnswerMatch[1].trim();
    remainingText = remainingText.replace(correctAnswerMatch[0], '').trim(); // Remove correct answer
  } else {
    parsed.correctAnswer = 'N/A';
  }

  // 4. Parse and remove Options (usually after the question)
  // Make sure the regex captures the options and leaves the question text before them
  const optionsMatch = remainingText.match(/(A\)\s*[\s\S]*?\nB\)\s*[\s\S]*?\nC\)\s*[\s\S]*?\nD\)\s*[\s\S]*)/);
  if (optionsMatch && optionsMatch[1]) {
    // Extract options into structured format
    const optionParts = optionsMatch[1].match(/([A-D])\)\s*([\s\S]*?)(?=\n[A-D]\)|\s*$)/g);
    if (optionParts) {
        parsed.options = {};
        optionParts.forEach(part => {
            const [_, letter, text] = part.match(/([A-D])\)\s*([\s\S]*)/) || [];
            if (letter && text) {
                parsed.options[letter] = text.trim();
            }
        });
    } else {
        parsed.options = null;
    }

    remainingText = remainingText.replace(optionsMatch[0], '').trim(); // Remove options block
  } else {
    parsed.options = null; // No options found
  }

  // 5. What's left should be the clean Question text
  // Look for "Question:" at the beginning of the remaining text
  const questionPrefixMatch = remainingText.match(/^Question:\s*([\s\S]*)/);
  if (questionPrefixMatch && questionPrefixMatch[1]) {
    parsed.question = questionPrefixMatch[1].trim();
  } else {
    // Fallback: If "Question:" prefix somehow got lost or isn't at start, just take what's left
    parsed.question = remainingText.trim();
  }

  return parsed;
};