// frontend/src/utils/dataParser.js

export const parseQuestionText = (questionText) => {
  const parsed = {};
  const questionMatch = questionText.match(/Question: ([\s\S]*?)\n[A-D]\)/);
  if (questionMatch) {
    parsed.question = questionMatch[1].trim();
  } else {
    parsed.question = questionText.split('\n')[0].replace('Question:', '').trim();
  }


  const optionsMatch = questionText.match(/A\) (.*)\nB\) (.*)\nC\) (.*)\nD\) (.*)/);
  if (optionsMatch) {
    parsed.options = {
      A: optionsMatch[1].trim(),
      B: optionsMatch[2].trim(),
      C: optionsMatch[3].trim(),
      D: optionsMatch[4].trim(),
    };
  }

  const correctAnswerMatch = questionText.match(/Correct Answer: (.*)/);
  if (correctAnswerMatch) {
    parsed.correctAnswer = correctAnswerMatch[1].trim();
  } else {
    parsed.correctAnswer = 'N/A'; // Provide a default if not found
  }

  const explanationMatch = questionText.match(/Explanation: ([\s\S]*)/);
  if (explanationMatch) {
    parsed.explanation = explanationMatch[1].trim();
  } else {
    // Provide a default empty string or a placeholder if no explanation is found
    parsed.explanation = 'No detailed explanation provided by the AI.';
  }

  return parsed;
};