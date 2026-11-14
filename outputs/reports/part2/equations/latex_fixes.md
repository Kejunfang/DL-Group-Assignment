# Part 2: LaTeX fixes (English text, LaTeX math)

## Inline replacements

### 2.12, first sentence
Old: Plain gradient descent updates each weight with w = w - lr * g, using only the current gradient g.
New: Plain gradient descent updates each weight by subtracting the learning rate times the gradient, \(w_{t+1} = w_t - \eta g_t\), using only the current gradient \(g_t\).

### 2.12, weight decay sentence
Old: at every step each weight is pulled slightly towards zero by lr  0.05  weight, independently of the moment estimates.
New: at every step each weight is pulled slightly towards zero in proportion to the learning rate and the weight, \(\eta \times 0.05 \times w\), independently of the moment estimates.

### 2.12, parameters after the update equation
Old: with beta1 = 0.9, beta2 = 0.999 and epsilon = 1e-7. Dividing by sqrt(v_hat) gives ...
New: with \(\beta_1 = 0.9\), \(\beta_2 = 0.999\) and \(\epsilon = 10^{-7}\), where \(\eta\) is the learning rate. Dividing by \(\sqrt{\hat{v}_t}\) gives ...

### 2.16, range of the true-class probability
Old: The probability assigned to the true class is between 0.007 and 0.014.
New: The probability assigned to the true class is between 0.0067 and 0.0143.

### 2.19, logits and ratio
Old: the logits z_1 (Benign) and z_2 (Malignant)
New: the logits \(z_1\) (Benign) and \(z_2\) (Malignant)

Old: if z_a - z_b = 2, class a is exp(2) = 7.39 times more likely than class b.
New: if \(z_a - z_b = 2\), class \(a\) is \(e^2 \approx 7.39\) times more likely than class \(b\).

Old: (z_k - max z)
New: \((z_k - \max_j z_j)\)

### 2.2, the gradient example
Old: y = w * x^2 + 1 with w = 3 (trainable) and x = 2 (input) ... y = 13 ... dy/dw = x^2 = 4
New: \(y = wx^2 + 1\) with \(w = 3\) (trainable) and \(x = 2\) (input) ... \(y = 13\) ... \(\mathrm{d}y/\mathrm{d}w = x^2 = 4\)

### 2.15, confusion matrix
Old: The matrix is [[0.98, 0.02], [0.35, 0.65]].
New: The matrix is
\[
\begin{bmatrix} 0.98 & 0.02 \\ 0.35 & 0.65 \end{bmatrix}.
\]

## Display equations

### 2.12, first moment
\[
m_t = \beta_1 m_{t-1} + (1-\beta_1) g_t
\]

### 2.12, second moment
\[
v_t = \beta_2 v_{t-1} + (1-\beta_2) g_t^2
\]

### 2.12, bias-corrected moments
\[
\hat{m}_t = \frac{m_t}{1-\beta_1^t}, \qquad
\hat{v}_t = \frac{v_t}{1-\beta_2^t}
\]

### 2.12, parameter update
\[
w_{t+1} = w_t - \eta \, \frac{\hat{m}_t}{\sqrt{\hat{v}_t} + \epsilon}
\]

### ensemble
\[
p_k = \frac{p_k^{\mathrm{ResNet50}} + p_k^{\mathrm{BiT}}}{2}
\]

### 2.19, softmax
\[
p_k = \frac{\exp(z_k)}{\sum_{j=1}^{2} \exp(z_j)}
\]

### 2.20, expected calibration error
\[
\mathrm{ECE} = \sum_{b=1}^{B} \frac{n_b}{n}
\left| \mathrm{acc}(b) - \mathrm{conf}(b) \right|
\]

## Google Docs note

The built-in equation editor (Insert > Equation) accepts a subset of LaTeX, such as \beta, \frac, \sqrt, \sum, ^ and _. It does not accept full LaTeX (for example accents such as \hat, or \mathrm). If you want to paste the display equations above as LaTeX, use the Auto-LaTeX Equations add-on (paste \( ... \) or $$ ... $$, then Render equations). Otherwise insert the equation images from the equations folder.
