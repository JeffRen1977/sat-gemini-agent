import React from 'react';
import './TimeManagementGuide.css';

const TimeManagementGuide = ({ onGoBack }) => {
  return (
    <div className="time-management-guide-container">
      <div className="guide-header">
        <h1>SAT Time Management Strategies</h1>
        <button onClick={onGoBack} className="back-button">Back to Dashboard</button>
      </div>

      <section className="guide-section">
        <h2>General SAT Time Management Tips</h2>
        <ul>
          <li>
            <strong>Know the Test Structure:</strong> Familiarize yourself with each SAT section, the number of questions, and the allotted time. This knowledge is the foundation of effective time management.
            <ul>
              <li>Reading: 65 minutes, 52 questions</li>
              <li>Writing and Language: 35 minutes, 44 questions</li>
              <li>Math (No Calculator): 25 minutes, 20 questions</li>
              <li>Math (Calculator): 55 minutes, 38 questions</li>
            </ul>
          </li>
          <li>
            <strong>Practice with a Timer Consistently:</strong> Every time you do practice sections or full tests, use a timer. This helps you get a feel for the pacing required.
          </li>
          <li>
            <strong>Don't Get Stuck:</strong> If a question is too difficult or time-consuming, make an educated guess (if you can eliminate options) and move on. You can mark it to return to if you have time at the end of the section.
          </li>
          <li>
            <strong>Answer Every Question:</strong> There is no penalty for guessing on the current SAT. Always fill in an answer for every question, even if it's a random guess.
          </li>
          <li>
            <strong>Pacing is Key:</strong>
            <ul>
                <li>Reading: About 1 minute 15 seconds per question (including passage reading time).</li>
                <li>Writing and Language: About 45-50 seconds per question.</li>
                <li>Math (No Calculator): About 1 minute 15 seconds per question.</li>
                <li>Math (Calculator): About 1 minute 25-30 seconds per question.</li>
            </ul>
            Remember these are averages; some questions will be quicker, others will take longer.
          </li>
          <li>
            <strong>Wear a Watch:</strong> You cannot rely on your phone. Bring a simple digital or analog watch (no smartwatches allowed).
          </li>
           <li>
            <strong>Bubble Strategically:</strong> Some students prefer to bubble answers after each question, others after each page, and some at the end of the section. Practice to see what works for you, but be careful not to make mistakes if bubbling in bulk at the end. Don't wait until the last minute.
          </li>
        </ul>
      </section>

      <section className="guide-section">
        <h2>Reading Section Strategies</h2>
        <ul>
          <li>
            <strong>Choose Your Passage Approach:</strong>
            <ul>
              <li><strong>Read Passage First:</strong> Thoroughly read the passage, then answer questions. Good if you're a strong reader.</li>
              <li><strong>Skim Passage, then Questions:</strong> Skim for main ideas, then look at questions. Refer back to the passage for details. A common, balanced approach.</li>
              <li><strong>Questions First (Caution):</strong> Look at questions (especially line-reference ones) then hunt for answers. Can be risky and lead to misunderstanding context.</li>
            </ul>
            Experiment during practice to find what suits you best.
          </li>
          <li>
            <strong>Skim Passages Effectively:</strong> Focus on the introduction, conclusion, and the first and last sentences of body paragraphs to grasp the main idea and structure.
          </li>
          <li>
            <strong>Focus on Main Ideas and Author's Purpose:</strong> Many questions will test your understanding of these broader concepts.
          </li>
          <li>
            <strong>Manage Time for Paired Questions:</strong> These questions (one asking about the passage, the next asking for evidence) can be tackled together. Find the evidence first, then answer the initial question.
          </li>
          <li>
            <strong>Don't Over-Analyze Unknown Words:</strong> Try to understand them from context. The SAT usually tests vocabulary through context rather than obscure definitions.
          </li>
        </ul>
      </section>

      <section className="guide-section">
        <h2>Writing and Language Section Strategies</h2>
        <ul>
          <li>
            <strong>Understand Common Grammar Rules:</strong> The SAT tests a predictable set of grammar rules (subject-verb agreement, pronoun agreement, punctuation, parallelism, modifiers, etc.). Master these.
          </li>
          <li>
            <strong>Quickly Identify Question Types:</strong> Recognize if a question is about punctuation, sentence structure, transitions, relevance, or graphical data.
          </li>
          <li>
            <strong>Read the Surrounding Sentences for Context:</strong> Don't just read the underlined portion. Context is crucial for many questions, especially those about transitions or adding/deleting sentences.
          </li>
          <li>
            <strong>"NO CHANGE" is Often Correct:</strong> Don't be afraid to pick "NO CHANGE" if the original sentence seems correct. It's a valid option.
          </li>
          <li>
            <strong>Trust Your Ear, but Verify with Rules:</strong> Sometimes what "sounds right" is correct, but always try to confirm with a specific grammar rule.
          </li>
        </ul>
      </section>

      <section className="guide-section">
        <h2>Math (No Calculator & Calculator) Section Strategies</h2>
        <ul>
          <li>
            <strong>Quickly Assess Calculator Use (Calculator Section):</strong> For the calculator section, decide if a calculator will actually save time. Sometimes mental math or by-hand calculation is faster.
          </li>
          <li>
            <strong>Don't Overuse the Calculator:</strong> It can slow you down if used for simple calculations. Be proficient with your calculator's functions beforehand.
          </li>
          <li>
            <strong>Use Problem-Solving Strategies:</strong>
            <ul>
              <li><strong>Plugging In Numbers:</strong> Useful for algebraic questions with variables in the answer choices. Pick simple numbers.</li>
              <li><strong>Backsolving:</strong> Start with answer choice C and plug it into the problem. Useful if answer choices are numerical.</li>
            </ul>
          </li>
          <li>
            <strong>Understand Formulas Provided:</strong> At the beginning of each math section, there's a reference box of formulas. Know what they are and how to use them, but also memorize key ones to save time.
          </li>
          <li>
            <strong>Grid-In Answers Carefully:</strong> Make sure you understand how to bubble in grid-in answers correctly, including fractions and decimals. Practice this.
          </li>
          <li>
            <strong>Show Your Work (Scratch Paper):</strong> Even if you're good at mental math, writing steps down can prevent careless errors, especially under pressure.
          </li>
        </ul>
      </section>

      <div className="guide-footer">
        <button onClick={onGoBack} className="back-button large-back-button">Back to Dashboard</button>
      </div>
    </div>
  );
};

export default TimeManagementGuide;
