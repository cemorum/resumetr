document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('json-form');
    const nameInput = document.getElementById('name');
    const numQuestionsInput = document.getElementById('num-questions');
    const questionsContainer = document.getElementById('questions');
    const addQuestionButton = document.getElementById('add-question');

    addQuestionButton.addEventListener('click', () => {
        const questionDiv = document.createElement('div');
        questionDiv.classList.add('question');
        
        const questionLabel = document.createElement('label');
        questionLabel.innerText = 'Question:';
        const questionInput = document.createElement('input');
        questionInput.type = 'text';
        questionInput.required = true;

        const numOptionsLabel = document.createElement('label');
        numOptionsLabel.innerText = 'Number of options:';
        const numOptionsInput = document.createElement('input');
        numOptionsInput.type = 'number';
        numOptionsInput.min = '1';
        numOptionsInput.required = true;

        const optionsContainer = document.createElement('div');
        optionsContainer.classList.add('options');

        const answerLabel = document.createElement('label');
        answerLabel.innerText = 'Correct answer:';
        const answerSelect = document.createElement('select');
        answerSelect.required = true;

        numOptionsInput.addEventListener('change', () => {
            const numOptions = numOptionsInput.value;
            optionsContainer.innerHTML = '';
            answerSelect.innerHTML = '';

            for (let i = 0; i < numOptions; i++) {
                const optionLabel = document.createElement('label');
                optionLabel.innerText = `Option ${i + 1}:`;
                const optionInput = document.createElement('input');
                optionInput.type = 'text';
                optionInput.required = true;

                optionInput.addEventListener('blur', () => {
                    const optionText = optionInput.value.trim();
                    if (optionText) {
                        if (answerSelect.children[i]) {
                            answerSelect.children[i].textContent = optionText;
                            answerSelect.children[i].value = optionText;
                        } else {
                            const answerOption = document.createElement('option');
                            answerOption.textContent = optionText;
                            answerOption.value = optionText;
                            answerSelect.appendChild(answerOption);
                        }
                    }
                });

                optionsContainer.appendChild(optionLabel);
                optionsContainer.appendChild(optionInput);
            }
        });

        questionDiv.appendChild(questionLabel);
        questionDiv.appendChild(questionInput);
        questionDiv.appendChild(numOptionsLabel);
        questionDiv.appendChild(numOptionsInput);
        questionDiv.appendChild(optionsContainer);
        questionDiv.appendChild(answerLabel);
        questionDiv.appendChild(answerSelect);

        questionsContainer.appendChild(questionDiv);
    });

    form.addEventListener('submit', (event) => {
        event.preventDefault();

        const jsonData = {
            name: nameInput.value,
            questions: [],
        };

        const questionElements = document.querySelectorAll('.question');
        questionElements.forEach((questionElement) => {
            const questionInput = questionElement.querySelector('input[type="text"]');
            const optionsInputs = questionElement.querySelectorAll('.options input[type="text"]');
            const answerSelect = questionElement.querySelector('select');

            const options = Array.from(optionsInputs).map(input => input.value);

            jsonData.questions.push({
                question: questionInput.value,
                options: options,
                answer: options[answerSelect.selectedIndex],
            });
        });
        const jsonBlob = new Blob([JSON.stringify(jsonData, null, 2)], { type: 'application/json' });
        const jsonUrl = URL.createObjectURL(jsonBlob);

        const downloadLink = document.createElement('a');
        downloadLink.href = jsonUrl;
        downloadLink.download = 'questions.json';
        downloadLink.style.display = 'none';
        document.body.appendChild(downloadLink);
        downloadLink.click();
        document.body.removeChild(downloadLink);
    });
});
