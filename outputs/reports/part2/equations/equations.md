# Part 2 equations (for the Google Doc)

The seven display equations of Part 2 are in this folder as 300 dpi PNG images rendered with the STIX font (the Times-compatible math font). In Google Docs, put the cursor where the equation belongs and use **Insert > Image > Upload from computer**. The images have a white background and can be resized by dragging a corner.

| Image | Section | Where it goes | LaTeX source | Plain-text fallback |
|:-----|:--------|:--------------|:-------------|:--------------------|
| eq1.png | 2.12 | after “keeps two running averages for every weight:” | m_t = \beta_1 m_{t-1} + (1-\beta_1) g_t | mₜ = β₁mₜ₋₁ + (1 − β₁)gₜ |
| eq2.png | 2.12 | after eq1 | v_t = \beta_2 v_{t-1} + (1-\beta_2) g_t^2 | vₜ = β₂vₜ₋₁ + (1 − β₂)gₜ² |
| eq3.png | 2.12 | after “they are bias-corrected as” | \hat{m}_t = \frac{m_t}{1-\beta_1^t}, \quad \hat{v}_t = \frac{v_t}{1-\beta_2^t} | m̂ₜ = mₜ/(1 − β₁ᵗ),  v̂ₜ = vₜ/(1 − β₂ᵗ) |
| eq4.png | 2.12 | after “and the update is” | w_{t+1} = w_t - \eta \frac{\hat{m}_t}{\sqrt{\hat{v}_t} + \epsilon} | wₜ₊₁ = wₜ − ηm̂ₜ/(√v̂ₜ + ε) |
| eq5.png | ensemble (after 2.13) | after “averages the softmax probabilities of the two members,” | p_k = \frac{p_k^{\mathrm{ResNet50}} + p_k^{\mathrm{BiT}}}{2} | p_k = (p_k(ResNet-50) + p_k(BiT))/2 |
| eq6.png | 2.19 | after “Softmax converts the two logits into probabilities with” | p_k = \frac{\exp(z_k)}{\sum_{j=1}^{2} \exp(z_j)} | pₖ = exp(zₖ)/Σⱼ₌₁² exp(zⱼ) |
| eq7.png | 2.20 | after “the weighted average of the gap between the two,” | \mathrm{ECE} = \sum_{b=1}^{B} \frac{n_b}{n} \left| \mathrm{acc}(b) - \mathrm{conf}(b) \right| | ECE = Σᵦ₌₁ᴮ (nᵦ/n)|acc(b) − conf(b)| |

In the Word draft the same images are already placed at these positions.


## Type-and-render option (Auto-LaTeX Equations add-on)

If you install the free **Auto-LaTeX Equations** add-on in Google Docs, paste each line below into the document as normal text, select it, then use **Add-ons > Auto-LaTeX Equations > Render equations**. The add-on converts the LaTeX into a rendered equation image.

```
$$m_t = \beta_1 m_{t-1} + (1-\beta_1) g_t$$

$$v_t = \beta_2 v_{t-1} + (1-\beta_2) g_t^2$$

$$\hat{m}_t = \frac{m_t}{1-\beta_1^t}, \qquad \hat{v}_t = \frac{v_t}{1-\beta_2^t}$$

$$w_{t+1} = w_t - \eta \frac{\hat{m}_t}{\sqrt{\hat{v}_t} + \epsilon}$$

$$p_k = \frac{p_k^{\mathrm{ResNet50}} + p_k^{\mathrm{BiT}}}{2}$$

$$p_k = \frac{\exp(z_k)}{\sum_{j=1}^{2} \exp(z_j)}$$

$$\mathrm{ECE} = \sum_{b=1}^{B} \frac{n_b}{n} \left| \mathrm{acc}(b) - \mathrm{conf}(b) \right|$$
```

The built-in Google Docs equation editor (Insert > Equation) also accepts a small set of LaTeX-style commands, but it is not a full LaTeX engine: `\beta`, `\frac`, `\sqrt`, `\sum`, `^` and `_` work, while accents such as `\hat` and text commands such as `\mathrm` may not. It also requires the text to be typed inside an equation box, and plain text in the body is never converted automatically.
