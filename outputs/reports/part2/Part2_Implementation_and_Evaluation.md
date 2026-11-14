# Part 2: Implementation and Evaluation

Part 2 implements the ResNet-50 chosen in Part 1.4 for domain option A, ISIC skin-lesion classification. Given a dermoscopy image and the patient metadata that comes with it (age, sex, body site), the system decides whether the lesion is benign or malignant. The final prediction averages the softmax probabilities of two ResNet-50 models with different pre-training: a Keras ResNet-50 with ImageNet-1k weights, trained at 448 x 448 pixels, and a BiT-M ResNet-50 with ImageNet-21k weights [1], trained at 384 x 384 pixels and evaluated at 448 x 448. All code is in the single notebook code/Group_8_Image_Recognition.ipynb, and the numbers and figures below come from running it from top to bottom on an Apple M4 GPU. The figure files are stored in outputs/run_448px_binary/figures/.

Three features of the setup affect how the results should be read.

* The task is binary, benign versus malignant, and replaces the original seven-class task. The datasets label eight diagnoses, and an earlier version of this project classified the seven diagnoses of HAM10000 directly (MEL, NV, BCC, AKIEC, BKL, DF, VASC). That version stopped at 85-86% accuracy because most errors were between melanoma, nevi and benign keratoses. The binary decision is also the one that matters in screening, so the task was changed; Section 2.4 gives the label mapping and Section 2.10 the earlier runs.
* HAM10000 is split by image, so the same lesion can appear in two splits. The dataset has 10,015 images of 7,470 lesions, which means some lesions have several photographs. With an image-level split, 36.7% of the validation images and 34.1% of the test images show a lesion that also has another photograph in the training set. This is data leakage. Section 2.4 quantifies it, and Section 2.14 reports accuracy separately for new lesions and for lesions seen in training, next to the result of an earlier lesion-level split.
* ISIC 2019 and BCN20000 contribute training images only. They are never used for validation, model selection or the test score, which comes only from HAM10000.

The final model reaches 91.48% test accuracy, against 80.51% for a model that always answers "Benign". Table 1 summarises the results.

**Table 1. Final results on HAM10000.** Validation and test accuracy are single evaluations with the weights of the best validation epoch; the test set is used once. The training accuracy of the final model was measured without augmentation on 2,000 random training images.

| Model | Validation accuracy | Test accuracy |
|:------|--------------------:|--------------:|
| ResNet-50 (ImageNet-1k, 448 px) | 0.8948 | 0.9035 |
| BiT-M ResNet-50 (ImageNet-21k, evaluated at 448 px) | 0.8975 | 0.9095 |
| **Final model (average of the two)** | **0.9075** | **0.9148** |
| Always-Benign baseline | 0.8049 | 0.8051 |

The final model reaches 94.7% training accuracy on HAM10000 training images and 94.0% on training images from all three sources. Its test malignant recall is 64.5% (melanoma 47.9%) and its test expected calibration error is 0.026.

## 2.1 Deep learning libraries

The implementation uses TensorFlow 2.18.1 and Keras 3.15.1, with no PyTorch. Keras supplies the layers, the keras.applications.ResNet50 backbone, the optimizer and model.fit; TensorFlow supplies the tensors, the tf.data input pipeline and tf.GradientTape. NumPy 2.0.2 and pandas 3.1 handle arrays and label tables. scikit-learn 1.9 provides the stratified split, the confusion matrix and the classification report, Matplotlib 3.11 and seaborn 0.13 produce the figures, and Pillow 13 reads the original JPEG files. Training runs on an Apple M4 GPU through tensorflow-metal 1.2.0.

Training ran in a local Anaconda environment inside Jupyter Notebook (conda dev-metal: Python 3.12, TensorFlow 2.18.1 with tensorflow-metal 1.2.0, Keras 3.15.1, NumPy 2.0.2). The notebook also detects Kaggle and can run on a free Kaggle GPU, but the results here come from the local Apple M4 GPU. A second environment without tensorflow-metal (conda dev, TensorFlow 2.21 on the CPU) runs the same notebook and was used to test the code.

## 2.2 How the framework tracks the forward pass for automatic differentiation

TensorFlow computes gradients with tf.GradientTape [2]. Inside a with tf.GradientTape() block, every operation on a trainable variable (multiplication, convolution, ReLU, softmax) is recorded together with its inputs and outputs. That recording is the forward pass. Calling tape.gradient(loss, variables) afterwards reads the tape in reverse and applies the chain rule to each recorded operation, which gives the derivative of the loss with respect to every trainable variable. This is reverse-mode automatic differentiation, the same principle as PyTorch's requires_grad=True and loss.backward(): PyTorch lets each tensor remember how it was created, while TensorFlow lets the tape remember it. Keras' model.fit() runs this sequence internally for every batch, from the forward pass and the loss to tape.gradient and optimizer.apply_gradients, so no training loop is written by hand.

The notebook demonstrates the mechanism on y = wx² + 1 with w = 3 (trainable) and x = 2 (input). The forward pass gives y = 13, and the tape returns dy/dw = x² = 4 because w appears only in the first term. The derivative therefore comes from the recorded operations rather than from a hand-written formula, and only variables declared as trainable receive a gradient. Layers frozen with trainable = False still pass the gradient to earlier layers, but their own weights do not change.

## 2.3 Training mode versus evaluation mode (memory)

The two modes differ in what the framework must keep in memory.

* In training mode the backward pass needs the intermediate activations, so the tape keeps the output of every convolution for every image in the batch, the gradients, and Adam's two moment vectors for every trainable weight. Dropout is active and BatchNorm would use batch statistics.
* In evaluation mode, model.predict() and model(x, training=False) run without a tape. An activation can be released as soon as the next layer has consumed it, and no gradients or optimizer states are created. Dropout is switched off and BatchNorm uses its stored running statistics. This is TensorFlow's equivalent of PyTorch's model.eval() with torch.no_grad(), and it uses much less memory, so inference can use larger batches than training.

In this model the backbone is always called with training=False, so its BatchNorm layers use their ImageNet statistics during fine-tuning as well, and BatchNorm weights are excluded from training. This keeps fine-tuning stable with the batch size of 16 that 448-pixel images allow: batch statistics from 16 images are noisy, and updating the BatchNorm statistics of a pre-trained network with them would damage the features. The notebook shows the behavioural difference with a Dropout layer: on a vector of eight ones, training=True returns values such as [2, 2, 0, 0, 0, 0, 0, 2] (about half of the units are dropped and the survivors are rescaled by two), while training=False returns [1, 1, 1, 1, 1, 1, 1, 1].

## 2.4 Data loading, preprocessing and label encoding

The experiments use three public data sources, listed in Table 2. HAM10000 [3, 4] provides the validation and test images and part of the training images. The ISIC 2019 training set [5] and BCN20000 [6] (the labelled part of the ISIC 2019 test set) are added to the training set only. The notebook reads the label CSV of each source, finds every image by its file name in any sub-folder, and checks that every image file exists.

**Table 2. Data sources and their role.** The ISIC 2019 training set contains the same 10,015 HAM10000 images under the same ISIC identifiers; those duplicates and images with the unknown diagnosis UNK are removed before training.

| Source | Role | Images used | Diagnoses |
|:-------|:-----|------------:|:----------|
| HAM10000 (ISIC 2018 Task 3) | training 7,010 / validation 1,502 / test 1,503, split by image 70/15/15, stratified by diagnosis | 10,015 | 7 |
| ISIC 2019 training set | extra training data only | 15,316 | 8 |
| BCN20000 (labelled ISIC 2019 test set) | extra training data only | 6,191 | 8 |

The training set has 28,517 images: 16,922 benign and 11,595 malignant (40.7% malignant). Validation (1,502 images) and test (1,503 images) contain only HAM10000 images. SCC appears only in the two extra datasets (596 training images), so it is learned but cannot be evaluated separately on the HAM10000 validation or test split. Figure 1 shows the class distribution of the three splits.

Each diagnosis is mapped to one of the two classes (Table 3), then to an integer index (Benign = 0, Malignant = 1), and finally to a one-hot vector (Benign = [1, 0], Malignant = [0, 1]) inside the tf.data pipeline, which is the target format of categorical cross-entropy. The diagnosis itself stays in a separate column and is used in Section 2.14 to see which diagnoses are missed most often.

**Table 3. Mapping from the eight dataset diagnoses to the two classes.**

| Diagnosis | Meaning | Class |
|:----------|:--------|:------|
| MEL | melanoma | Malignant |
| BCC | basal cell carcinoma | Malignant |
| AKIEC | actinic keratosis / intraepithelial carcinoma | Malignant |
| SCC | squamous cell carcinoma | Malignant |
| NV | melanocytic nevus | Benign |
| BKL | benign keratosis-like lesion | Benign |
| DF | dermatofibroma | Benign |
| VASC | vascular lesion | Benign |
| UNK | unknown diagnosis | dropped |

The original label space had seven classes (MEL, NV, BCC, AKIEC, BKL, DF and VASC), and the first version of this project trained a ResNet-50 to predict them. Those runs reached only 85-86% accuracy, and the confusion matrices showed that most errors were between melanoma, nevi and benign keratoses, which look very similar. Grouping the seven-class predictions into benign and malignant raised accuracy to about 90% on validation and 91% on test. The binary decision (does this lesion need a biopsy?) is also the clinically meaningful output of a screening system. The task was therefore changed to benign versus malignant: SCC was added as a malignant class, AKIEC is counted as malignant because actinic keratosis is a precancerous lesion and intraepithelial carcinoma is an early cancer, and images with UNK are dropped. Section 2.10 still reports the seven-class runs. The change alters the task definition of the assignment, although the datasets are unchanged, and the group agreed to it.

The original images are up to 1024 pixels wide. Decoding and resizing them in every epoch would waste time, so every image is resized once to 448 x 448 and stored as a JPEG under outputs/resized_448/; a 384 x 384 copy is stored for the BiT member. Later runs reuse the cache. ResNet-50 was pre-trained at 224 x 224, but a convolutional network accepts any input size, and 448 x 448 keeps more of the fine structures (dots, streaks, pigment network) that separate the classes. The pipeline reads a small JPEG, converts it to float32 (pixel values stay in 0-255), attaches the 10-number metadata vector, converts the label to one-hot encoding, and batches 16 images. The training set is shuffled every epoch. The ResNet-specific preprocessing (RGB to BGR and subtraction of the ImageNet channel means) is applied inside the model, so the same model accepts raw images at prediction time.

Age, sex and body site are recorded for every image in the three datasets, so they are used as a second input. Each image receives a 10-number vector: age divided by 100, a flag for missing age, one-hot sex (male, female) and one-hot body-site group (torso, head/neck, upper extremity, lower extremity, palms/soles, oral/genital). The three datasets name body sites differently, so the names are mapped to the six groups; unknown values are encoded as zeros. The vector is concatenated with the pooled image features in Section 2.7.

Four augmentation layers are active only during training: random horizontal and vertical flips, random rotation up to plus or minus 90 degrees, random zoom up to 15%, and random brightness and contrast changes up to 10% (colour jitter). Section 2.5 shows examples. A skin lesion has no natural "up" direction, and photographs are taken with different cameras and lighting, so all four changes produce realistic new images of the same lesion.

About 80% of the validation and test images are benign, so a model that always answers "Benign" already reaches 80.49% on validation and 80.51% on test (Table 1). Accuracy alone is not enough. The final model has to be clearly better than this baseline, and Section 2.14 also reports the malignant recall, because a missed melanoma is the most serious error.

HAM10000 contains 10,015 images of 7,470 lesions, so 2,545 images are repeat photographs of a lesion that also has another photograph in the dataset. The split is stratified by diagnosis at the image level rather than by lesion. As a result, 36.7% of the validation images (551 of 1,502) and 34.1% of the test images (512 of 1,503) show a lesion that also appears in the training set. This is data leakage: the model may have memorised the lesion rather than learned general features. Section 2.14 therefore reports accuracy separately for new lesions and for lesions seen in training, and compares it with the result of an earlier lesion-level split. Here the leakage does not inflate the score. The seen-lesion images are harder: 32.6% of the seen-lesion test images are malignant against 12.7% of the new-lesion test images, because lesions with several photographs are disproportionately melanomas (19.6% of the images of multi-image lesions are melanomas, against 11.1% of all HAM10000 images).

![Figure 1: Number of training, validation and test images per class. The training bars include ISIC 2019 and BCN20000; the validation and test bars contain HAM10000 images only.](../run_448px_binary/figures/class_distribution.png)

## 2.5 One batch through the pipeline and two random augmentations

The notebook takes one batch from the training pipeline and prints its shapes. The image batch has shape (16, 448, 448, 3) with dtype float32 and pixel values between 0 and 252; the metadata batch has shape (16, 10), and its first row is [0.85, 0, 0, 1, 0, 0, 0, 1, 0, 0], i.e. age 85, female, lower extremity. The label batch has shape (16, 2); the first label is [0, 1], i.e. Malignant.

The same cell applies two single augmentations to one training image and displays both next to the original: a random rotation and colour jitter (brightness and contrast). A fourth panel shows the full pipeline (flip, rotation, zoom, colour jitter) applied once, and Figure 2 gives the result. The lesion and its label ("Malignant") stay the same in all four panels; only geometry and colour change.

![Figure 2: One training image (left) and the same image after a random rotation, after colour jitter, and after the full training augmentation. The label is unchanged in all four panels.](../run_448px_binary/figures/augmentation_examples.png)

## 2.6 How augmentation adds variance without changing the label

Every epoch the network sees a slightly different version of each training image: rotated, flipped, zoomed, a little brighter or with more contrast. The diagnosis does not depend on these properties: a melanoma rotated by 40 degrees, mirrored, or photographed under slightly different light is still a melanoma, so the one-hot label stays the same while the pixel values change. In this sense the augmentation increases the variance of the training data without changing the labels, and it enlarges the effective size of the training set.

The network therefore cannot memorise the exact pixels of a photograph; to fit the augmented copies it must learn features that are stable under the transformations, such as colour patterns, borders and structures inside the lesion, which reduces overfitting. The transformations were chosen so that they cannot change the diagnosis: there are no strong colour shifts (colour is an important clinical cue), no crops that could cut the lesion out of the image, and no elastic distortions that would create patterns which do not occur on skin. Section 2.10 explains why the final recipe uses this mild setting.

## 2.7 Building the model (ResNet-50 with transfer learning)

The model has two inputs, image and metadata. The image first passes through the augmentation layers, then through the ResNet preprocessing (RGB to BGR, subtract ImageNet means), and then through keras.applications.ResNet50 with ImageNet weights and without its 1000-class top layer [7]. At 448 x 448 the backbone turns the image into a 14 x 14 x 2048 block of features. A global average pooling layer reduces this to 2048 numbers, dropout 0.3 is applied, and the 10 metadata numbers are concatenated to give a 2058-number vector. A dense layer with two outputs produces the logits, and a softmax layer turns them into class probabilities. Table 4 is the model summary printed by the notebook (the ResNet-50 backbone is shown as one nested functional layer).

In stage 1 the model has 4,118 trainable parameters (the dense layer and its bias) and 23,587,712 non-trainable parameters. In stage 2 the BatchNorm layers remain frozen, so 23,485,590 parameters become trainable. The model is built with the functional API because the metadata is a second input and because the same layers are reused by the BiT member.

**Table 4. Model summary (Keras, 448 px input).** The backbone is frozen in stage 1; in stage 2 its convolutional layers are trained and its BatchNorm layers stay frozen.

| Layer | Output shape | Parameters | Trainable in stage 1 |
|:------|:-------------|-----------:|:--------------------:|
| image (InputLayer) | (None, 448, 448, 3) | 0 | - |
| augmentation (Sequential) | (None, 448, 448, 3) | 0 | - |
| resnet_preprocessing (Lambda) | (None, 448, 448, 3) | 0 | - |
| resnet50 (Functional) | (None, 14, 14, 2048) | 23,587,712 | no |
| global_avg_pool (GlobalAveragePooling2D) | (None, 2048) | 0 | - |
| dropout (Dropout) | (None, 2048) | 0 | - |
| metadata (InputLayer) | (None, 10) | 0 | - |
| image_and_metadata (Concatenate) | (None, 2058) | 0 | - |
| logits (Dense) | (None, 2) | 4,118 | yes |
| probabilities (Softmax) | (None, 2) | 0 | - |
| **Total** | | **23,591,830** | **4,118 trainable** |

Part 1.4 justified the choice of ResNet-50. Residual connections give the gradient an identity path to the earliest layers, so a 50-layer network can be fine-tuned without the vanishing-gradient problems of a plain deep stack. ResNet-50 is the smallest ResNet variant that is still deep enough for ImageNet features to transfer well, and its 24 million weights fit the 16 GB memory of the training machine at 448 pixels. The second member of the final ensemble is also a ResNet-50 (see the section after 2.13), so the system stays inside the backbone family chosen in Part 1.4.

## 2.8 Feature maps from a hidden layer

The notebook passes one test image (ISIC_0033892, a benign lesion) through the backbone and extracts the 112 x 112 x 256 feature map produced by conv2_block3_out, the end of the first residual stage. Figure 3 shows 16 of the 256 channels. Bright regions are positions where that filter responds strongly. The channels react to different low-level properties: some follow the border of the lesion (channels 2, 5 and 12), some the skin texture and fine lines (channels 1, 9 and 15), and one (channel 14) separates the lesion from the surrounding skin. Several channels are almost inactive on this image. This is expected at this depth: the first stage detects edges, colour blobs and boundaries, and later stages combine them into lesion-level patterns.

![Figure 3: Input image (left) and 16 of the 256 feature maps produced by conv2_block3_out at 112 x 112 (right). Each map is one filter channel.](../run_448px_binary/figures/feature_maps.png)

## 2.9 Why spatial size shrinks and channel depth grows, and how backpropagation updates the weights

ResNet-50 starts with a stride-2 convolution and a max-pool, which take 448 x 448 to 112 x 112, and each new stage begins with a stride-2 convolution that halves the resolution again. Table 5 shows the output shape at the end of each stage: 224 x 224 x 64, 112 x 112 x 256, 56 x 56 x 512, 28 x 28 x 1024 and 14 x 14 x 2048. The expanding channel dimension is the other half of the design.

**Table 5. Output shape at the end of each ResNet-50 stage for a 448 x 448 input.**

| Stage | Layer | Height | Width | Channels |
|:------|:------|-------:|------:|---------:|
| stem | conv1_relu | 224 | 224 | 64 |
| stage 1 | conv2_block3_out | 112 | 112 | 256 |
| stage 2 | conv3_block4_out | 56 | 56 | 512 |
| stage 3 | conv4_block6_out | 28 | 28 | 1024 |
| stage 4 | conv5_block3_out | 14 | 14 | 2048 |

Each position in a deeper map covers a larger part of the input image, i.e. it has a larger receptive field, and it combines the simpler features of earlier layers into more complex ones: edge, then texture, then pigment network, then whole-lesion pattern. Fewer positions are needed because the information is more abstract and spatially invariant, but more channels are needed because there are more kinds of complex patterns than kinds of edges. Halving the height and width while doubling the channels also keeps the computation per stage roughly constant, which is why a deep network remains trainable. The bottleneck blocks apply the same idea inside a stage: the 1 x 1 layers reduce and then restore the channel depth, so the expensive 3 x 3 convolution works on fewer channels.

The forward pass computes the predictions and the cross-entropy loss. The backward pass applies the chain rule from the output layer towards the input to obtain the gradient of the loss with respect to every trainable weight (Section 2.2). The optimizer then moves every weight a small step in the direction that lowers the loss (Section 2.12). Frozen layers still pass the gradient through to the layers before them, but their own weights do not change; this is why the fine-tuned ResNet-50 has 23.5 million trainable parameters in stage 2 while the BatchNorm layers keep their ImageNet values.

## 2.10 Training with an adaptive optimizer

Training has two stages, a standard transfer-learning recipe (Table 6). In stage 1 the backbone is frozen and only the randomly initialised head is trained, so that the large gradients of a new head do not damage the pre-trained filters. In stage 2 the whole backbone is fine-tuned with a small learning rate that decays with a cosine schedule, while the BatchNorm layers remain frozen (Section 2.3). The loss is categorical cross-entropy, computed on the softmax output, which pairs the output activation with the loss as discussed in Part 1.4. The training set is 28,517 images, i.e. 1,783 steps per epoch at batch size 16. Training on the Apple M4 GPU took about 7.5 hours for the ResNet-50 member and about 6 hours for the BiT member.

**Table 6. Training recipe.** The learning rate decays from 5e-5 to 1e-6 with a cosine schedule over the 10 fine-tuning epochs.

| Setting | Stage 1 | Stage 2 |
|:--------|:--------|:--------|
| Epochs | 2 | 10 |
| Trainable layers | new head only (4,118 weights) | head + all ResNet-50 convolutional layers, BatchNorm frozen (23,485,590 weights) |
| Optimizer | Adam, learning rate 1e-3 | Adam, learning rate 5e-5 decaying to 1e-6 (cosine) |
| Weight decay | 0.05 | 0.05 |
| Loss | categorical cross-entropy | categorical cross-entropy |
| Batch size | 16 | 16 |
| Augmentation | flips, rotation, zoom, colour jitter (training only) | same |
| Model selection | - | best validation accuracy; the test set is used once, at the end |
| Seed | 8 | 8 |

The final recipe came from a sequence of controlled changes, each diagnosed from the previous learning curves.

* The first seven-class run (224 x 224, only conv4 and conv5 fine-tuned) reached 85.3% validation and 84.2% test accuracy, started overfitting after epoch 9 and confused melanoma with nevi; test-time augmentation and class-threshold tuning gained less than one point.
* Raising the resolution to 384 x 384 and fine-tuning the whole backbone gave 86.1% validation and 86.0% test accuracy with a lesion-level split, and 85.8% validation and 87.6% test accuracy with the image-level split. Stronger regularisation (dropout 0.5, label smoothing 0.1, stronger augmentation) removed the overfitting but left the accuracy at 85.1% validation and 86.4% test; patient metadata and a third stage did not help, a deeper ResNet-152 reached 85.6% validation and 86.4% test, and an InceptionV3 reached 83.6% validation.
* The seven-class models all stopped at 85-86%, so the task was changed to two classes (Section 2.4). The first binary run (stronger regularisation, 8 fine-tuning epochs) reached 89.2% validation and 90.2% test accuracy but was underfitting (training accuracy 88.6% below validation accuracy); weakening the regularisation and fine-tuning for 12 epochs gave 89.1% validation and 89.8% test, and fine-tuning the whole backbone for 10 epochs gave 89.6% validation and 90.4% test.
* Raising the input to 448 x 448 gave 89.5% validation and 90.4% test accuracy. No single member crossed 90% validation accuracy at the 448-pixel evaluation; in the earlier single-model runs, test-time augmentation and a third training stage added at most 0.2 points, so the improvement was sought in a second model. The final ensemble of two differently pre-trained ResNet-50 models reaches 90.75% validation and 91.48% test accuracy.

The training loss is measured with augmentation and dropout, whereas the validation loss is not; this is why the training loss is higher than the validation loss at the start and why the two curves cross. Every epoch is logged to a CSV file, and a BackupAndRestore callback saves a backup after each epoch, so an interrupted kernel resumes from the last finished epoch when the notebook is run again. Finished stages are skipped, which makes the evaluation reproducible without retraining.

## 2.11 Training and validation loss curves with the learning-rate trajectory

Figure 4 has the training and validation cross-entropy loss on the left axis and the learning rate on the right axis (log scale), together with the accuracy curves. The dotted line marks the start of fine-tuning; the star marks the epoch whose weights are kept (epoch 12).

Both losses fall over the 12 epochs. Over the two head-only epochs the validation loss moves from 0.338 to 0.363 at a learning rate of 1e-3, and the validation accuracy is already about 0.849 because the ImageNet features are strong. At epoch 3 the learning rate drops to 5e-5 and the validation accuracy temporarily falls to 0.817, because the whole backbone is being adapted and the frozen head has to adjust; from epoch 4 onward both accuracy and loss improve steadily. The training loss falls from 0.520 to 0.239, while the validation loss falls to 0.259 (its minimum at epoch 9) and then stays between 0.26 and 0.28. The accuracy panel also shows the training accuracy catching up with and passing the validation accuracy, the beginning of overfitting (Section 2.13).

![Figure 4: Training and validation loss with the learning-rate schedule, and the accuracy curves, for the ResNet-50 member. The dotted line marks the start of fine-tuning and the star the kept epoch.](../run_448px_binary/figures/learning_curves.png)

## 2.12 How Adam uses past gradient information (moments)

Plain gradient descent updates each weight by subtracting the learning rate times the gradient, w ← w − ηg, using only the current gradient g. Adam (Adaptive Moment Estimation) [8] keeps two running averages for every weight:

$$m_t = \beta_1 m_{t-1} + (1-\beta_1) g_t$$

$$v_t = \beta_2 v_{t-1} + (1-\beta_2) g_t^2$$

The first moment m is an average of recent gradients, like momentum: noise from individual batches cancels out and the update keeps moving in a consistent direction. The second moment v is an average of recent squared gradients, i.e. an estimate of how large the gradient of this weight usually is. Both averages start at zero, so they are bias-corrected as

$$\hat{m}_t = \frac{m_t}{1-\beta_1^t}, \qquad \hat{v}_t = \frac{v_t}{1-\beta_2^t}$$

and the update is

$$w_{t+1} = w_t - \eta\,\frac{\hat{m}_t}{\sqrt{\hat{v}_t} + \epsilon}$$

with β₁ = 0.9, β₂ = 0.999 and ε = 1e-7. Dividing by the square root of the second moment gives every weight its own adaptive step: a weight with large, noisy gradients takes smaller steps, and a weight with small but consistent gradients takes larger ones. This is why Adam needs little tuning and is a common choice for fine-tuning pre-trained networks. The global learning rate still sets the overall step size, so it is reduced during fine-tuning.

The optimizer also uses a decoupled weight decay of 0.05 (the AdamW variant): at every step each weight is pulled slightly towards zero, in proportion to the learning rate and the weight (η × 0.05 × w), independently of the moment estimates. This keeps the fine-tuned filters small unless the data really needs them, a second form of regularisation besides dropout and augmentation. The final recipe has no label smoothing, because an earlier binary run with label smoothing was underfitting (Section 2.10).

## 2.13 Analysis of the loss curves

Three patterns matter when reading Figure 4.

* Underfitting appeared in the first binary run: training accuracy (88.6%) stayed below validation accuracy (89.2%), because the regularisation was too strong for the short schedule. Weakening it and fine-tuning longer fixed this (Section 2.10).
* No plateau appears in the ResNet-50 curves. Both losses are still moving at epoch 12, and the learning rate reaches 1e-6 only in the last epoch. The BiT member also improves until the last epoch.
* Overfitting starts after epoch 9. The lowest validation loss is 0.2593 at epoch 9; it rises to 0.2704 at epoch 12 while the training loss falls from 0.2959 to 0.2390. The best validation accuracy (0.8948) is reached at epoch 12, so accuracy and loss select different epochs; we keep the best validation accuracy because that is the metric the assignment asks for. The final gap between training and validation accuracy is only 0.39 percentage points, so the overfitting is mild.

The BiT curves behave similarly (Figure 5). Its training accuracy climbs to 0.9551, its validation loss is lowest at epoch 9 (0.2362) and rises afterwards, and its best validation accuracy (0.9048 at 384 px) is reached at epoch 12. The gap between training and validation accuracy is about 5 percentage points at the end, larger than for the ResNet-50, which is expected because the stronger ImageNet-21k features fit the training set faster.

## The second ResNet-50 and the final ensemble

At 448 pixels, the resolution used for the final model, neither member reaches 90% validation accuracy: the ResNet-50 reaches 0.8948 and the BiT-M ResNet-50 0.8975, or 0.9048 when evaluated at its training resolution of 384 pixels. Two models pre-trained on different data and trained with different frozen layers make partly different mistakes, so their average is usually better than either member. The final model therefore averages the softmax probabilities of the two members,

$$p_k = \frac{p_k^{\mathrm{ResNet50}} + p_k^{\mathrm{BiT}}}{2}$$

where both members are loaded with the weights of their best validation epoch and receive the same 448 x 448 image and metadata. The BiT member was trained at 384 pixels but is evaluated at 448 pixels: with global average pooling a convolutional network accepts any input size, and evaluating at a slightly higher resolution than in training usually helps a little [9].

The BiT-M R50x1 model ("Big Transfer" [1]) is a ResNet-50 pre-trained by Google on ImageNet-21k (about 14 million images of 21,843 classes) instead of ImageNet-1k. Keras does not provide it, so the notebook builds it layer by layer and loads Google's weights from the timm model hub on Hugging Face. It has the same bottleneck blocks as the Keras ResNet-50 (3 + 4 + 6 + 3 blocks, 1 x 1 then 3 x 3 then 1 x 1 convolutions, 2048 output channels) with three differences. Pre-activation places normalisation and ReLU before each convolution, so the shortcut is a clean identity. Group Normalization with 32 groups replaces BatchNorm, so each image is normalised on its own, independent of the batch size. Weight standardisation scales each kernel to zero mean and unit variance before use. The pixels are scaled to [-1, 1]. The backbone has 187 layers and 23,500,352 weights, and the head is the same as before. The recipe is identical to Table 6, with two changes that keep training within about 6 hours on the M4 GPU: the images are 384 x 384, and in stage 2 the stem and the first two stages stay frozen, so only stages 3 and 4 and the head are fine-tuned (22,062,102 trainable weights).

Figure 5 gives the BiT learning curves, and Table 1 compares the two members with the average.

![Figure 5: Learning curves of the BiT-M ResNet-50 member (loss and accuracy). The dotted line marks the start of fine-tuning and the star the kept epoch (12).](../run_448px_binary/figures/bit_learning_curves.png)

On validation, the average is 1.00 percentage point above the better member (the BiT model at 448 px) and 1.27 points above the ResNet-50; on test it is 0.53 points above the better member and 1.13 points above the ResNet-50. Measured without augmentation on 2,000 random training images, the final model reaches 94.7% training accuracy on HAM10000 and 94.0% on all three sources. These values are close to the augmented training curves, and the gap to test accuracy is about three points, so the ensemble has not simply memorised the training set.

## 2.14 Test accuracy and test loss

The final model is evaluated once on the 1,503 HAM10000 test images, which were not used for training or model selection. Test accuracy is **0.9148 (91.48%)** and test loss is **0.2021**; the ResNet-50 member alone reaches 0.9035 and the BiT member alone 0.9095. The always-Benign baseline on this split is 0.8051, so the final model lowers the error rate from 19.49% to 8.52%, a reduction of 56%.

Table 7 gives the classification report. The benign class has high recall (0.980) and precision (0.919); the malignant class has high precision (0.887) but much lower recall (0.645). The model finds 189 of the 293 malignant test lesions and misses 104, while it labels 24 of the 1,210 benign lesions as malignant. Sections 2.15 and 2.17 examine the low malignant recall.

**Table 7. Test classification report (1,503 images).**

| Class | Precision | Recall | F1-score | Support |
|:------|----------:|-------:|---------:|--------:|
| Benign | 0.919 | 0.980 | 0.949 | 1,210 |
| Malignant | 0.887 | 0.645 | 0.747 | 293 |
| Accuracy | | | 0.915 | 1,503 |
| Macro average | 0.903 | 0.813 | 0.848 | 1,503 |
| Weighted average | 0.913 | 0.915 | 0.909 | 1,503 |

Table 8 breaks the test accuracy down by diagnosis. The model is almost perfect on nevi (0.987) and vascular lesions (1.000), good on benign keratoses (0.958) and basal cell carcinomas (0.896), and weakest on melanomas (0.479) and dermatofibromas (0.765). Of the 104 missed malignant lesions, 87 are melanomas, 8 are basal cell carcinomas and 9 are actinic keratoses, so melanoma dominates the missed lesions. SCC is not in the HAM10000 test split and cannot be evaluated.

**Table 8. Test accuracy per diagnosis.**

| Class | Diagnosis | Test images | Accuracy |
|:------|:----------|------------:|---------:|
| Benign | BKL | 165 | 0.958 |
| Benign | DF | 17 | 0.765 |
| Benign | NV | 1,006 | 0.987 |
| Benign | VASC | 22 | 1.000 |
| Malignant | AKIEC | 49 | 0.816 |
| Malignant | BCC | 77 | 0.896 |
| Malignant | MEL | 167 | 0.479 |

Because the split is by image (Section 2.4), Table 9 separates the images of lesions that also have a photograph in the training set from the images of new lesions. New-lesion accuracy is 0.9425 on the test set, while accuracy on lesions seen in training is 0.8613. The leakage therefore does not inflate the test score: the seen-lesion test images are harder, because 32.6% of them are malignant against 12.7% of the new-lesion test images, and lesions with several photographs are disproportionately melanomas. The validation split shows the same pattern (0.9264 for new lesions, 0.8748 for seen lesions).

**Table 9. Accuracy by leakage status.** "Seen in training" means that the lesion of the image also has another photograph in the training set.

| Split | All images | New lesions | Lesions seen in training |
|:------|-----------:|------------:|-------------------------:|
| Validation (1,502 images) | 0.9075 | 0.9264 (951 images) | 0.8748 (551 images) |
| Test (1,503 images) | 0.9148 | 0.9425 (991 images) | 0.8613 (512 images) |

For new patients, the more honest estimate is a lesion-level split, in which no lesion appears in two splits. An earlier seven-class ResNet-50 version of this project, trained at 384 px on a lesion-level split, reached 0.8613 validation and 0.8595 test accuracy. That run is the best available estimate of performance on completely new lesions. The binary image-level result of 0.9148 should be read with it in mind, because about a third of its test images are repeat photographs of training lesions.

## 2.15 Normalized confusion matrix

Figure 6 is the confusion matrix of the final model on the test set, normalised by the true class, so each row sums to one and the diagonal entries are the recalls. The matrix is [[0.98, 0.02], [0.35, 0.65]]: 98% of the benign images are correctly classified and 2% become false positives, while only 65% of the malignant images are found and 35% become false negatives. In counts, 1,186 benign images are correct and 24 are false positives, while 189 malignant images are correct and 104 are false negatives.

The asymmetry between the two classes matters more than the overall accuracy. The model is conservative: it rarely calls a benign lesion malignant (precision 0.887), but it misses a third of the malignant lesions. In screening, a false negative costs much more than a false positive: a missed melanoma can be fatal, while a false positive usually leads to a benign biopsy. The 0.5 threshold on the softmax probability is the default and was not tuned; lowering it would trade precision for recall. Keeping the default makes the accuracy and calibration results comparable with the baseline. Section 2.17 discusses which lesions are missed.

![Figure 6: Normalized confusion matrix of the final model on the HAM10000 test set. Rows are normalised by the true class, so the diagonal gives the recall.](../run_448px_binary/figures/confusion_matrix.png)

## 2.16 Top 3 most confident wrong predictions

The notebook selects the three wrongly classified test images on which the model was most confident. All three are melanomas classified as benign with a probability of about 0.99 (Table 10 and Figure 7). The probability assigned to the true class is between 0.0067 and 0.0143, so the model is confidently wrong.

**Table 10. The three most confident wrong predictions on the test set.**

| Image | True diagnosis | True class | Predicted | Confidence | Probability of the true class |
|:------|:---------------|:-----------|:----------|-----------:|-----------------------------:|
| ISIC_0033300 | MEL | Malignant | Benign | 0.9933 | 0.0067 |
| ISIC_0033452 | MEL | Malignant | Benign | 0.9883 | 0.0117 |
| ISIC_0033154 | MEL | Malignant | Benign | 0.9857 | 0.0143 |

The three images in Figure 7 are small, brown, roughly round lesions with a fairly regular border, photographed on light skin. Two of them look very much like an ordinary nevus, and the third is partly covered by hairs that cross the lesion. The visual evidence is ambiguous in these cases, and the model's confidence shows that it has not learned to recognise its own uncertainty on them.

![Figure 7: The three test images on which the model was most confident and wrong. All three are melanomas predicted as benign with a probability of about 0.99.](../run_448px_binary/figures/top3_confident_errors.png)

## 2.17 Error analysis

The confusion matrix, the per-diagnosis accuracy and the three images above point to five causes of error.

* Melanoma and benign nevus overlap visually. Both can be brown, round lesions with a pigment network, and early melanomas often look like ordinary moles. This is the dominant error: 87 of the 104 missed malignant lesions are melanomas, and the melanoma recall (0.479) is far below the recall of every other diagnosis.
* The classes are imbalanced. About 80% of the test images are benign and 40.7% of the training images are malignant. When the evidence is unclear, the network has learned that "Benign" is the safer guess, which produces confident false negatives; the benign recall (0.980) and the malignant recall (0.645) show this.
* Artefacts and background obscure the lesion. Hairs, air bubbles, ruler marks and ink cover parts of the lesion or imitate its patterns. The third confident error in Figure 7 has several hairs crossing the lesion, and the feature maps in Section 2.8 respond to the lesion outline and skin texture rather than to the clinical pattern inside the lesion.
* Lighting and colour vary between images. Different cameras and lighting change the colour and contrast of the same kind of lesion; the augmentation includes mild brightness and contrast changes, but unusual lighting can still mislead the model.
* Resizing loses detail. At 448 x 448 some fine details of small lesions are removed, including irregular dots or streaks at the border that can separate a melanoma from a nevus.

The explanations above come from what is visible in the images and from the aggregate statistics; they do not prove what the network attended to. A saliency or Grad-CAM analysis would be needed to confirm individual cases. The model is a useful screening aid, not a replacement for a dermatologist: its high precision means a malignant prediction is usually correct, and its low recall means a benign prediction cannot rule out melanoma.

## 2.18 Class probabilities for an unseen test image

The notebook samples one image from the test split (never used for training or model selection) and predicts its class probabilities with the final model. The selected image, ISIC_0034059, is a melanoma on the upper extremity of a 70-year-old male. The final model assigns a probability of 0.9554 to Malignant and 0.0446 to Benign, and Figure 8 shows the image with the horizontal bar chart. The prediction is correct, and the two probabilities sum to one, as the softmax output requires. A single image illustrates the output; the aggregate results are in Section 2.14.

![Figure 8: An unseen test image (true class Malignant, melanoma) and the final model's softmax probabilities as a horizontal bar chart.](../run_448px_binary/figures/unseen_image_prediction.png)

## 2.19 From logits to probabilities with Softmax

The last dense layer outputs one raw score per class, the logits z₁ (Benign) and z₂ (Malignant). A logit can be any real number: it is a score, not a probability. Softmax converts the two logits into probabilities with

$$p_k = \frac{\exp(z_k)}{\sum_{j=1}^{2} \exp(z_j)}$$

The exponential makes every value positive and preserves the order of the scores, so a larger logit gives a larger probability; dividing by the sum makes the probabilities add up to one. Differences between logits become ratios: when one logit is 2 above the other, the corresponding class is exp(2) = 7.39 times more likely. The maximum logit is subtracted first (zₖ − max z), which gives the same result and avoids overflow.

The notebook reads the logits of the unseen image from the logits layer of the ResNet-50 member and applies the formula by hand (Table 11). The logits are -1.9543 and 2.0905; after subtracting the maximum, the exponentials are 0.0175 and 1.0000, so the hand-made softmax is [0.0172, 0.9828], which matches the ResNet-50 output exactly. The BiT member outputs [0.0719, 0.9281] for the same image, and the final model averages the two probability vectors to [0.0446, 0.9554], the value shown in Figure 8. The two members disagree slightly, and the average lies between them.

**Table 11. Hand calculation of the softmax for the unseen image, compared with the model outputs.**

| Quantity | Benign | Malignant |
|:---------|-------:|----------:|
| Logit z | -1.9543 | 2.0905 |
| exp(z - max z) | 0.0175 | 1.0000 |
| Softmax by hand | 0.0172 | 0.9828 |
| ResNet-50 output | 0.0172 | 0.9828 |
| BiT output | 0.0719 | 0.9281 |
| Final output (average) | 0.0446 | 0.9554 |

## 2.20 Overconfidence and calibration

A model is well calibrated if its confidence matches how often it is correct: among all predictions made with about 80% confidence, about 80% should be correct. Neural networks are often overconfident for three reasons. Cross-entropy keeps rewarding the model for pushing the correct logit higher, so after many epochs the logits become large and softmax outputs probabilities close to one even on hard images. Softmax has to spread 100% over the known classes and has no way to say "I do not know", so an unusual image can receive a high probability for a wrong class. Finally, training and test images come from different hospitals, cameras and lighting conditions, but the confidence does not take this distribution shift into account.

Figure 9 is the reliability diagram of the final model on the test set. The test predictions are grouped into 10 confidence bins, and for each bin the average confidence is compared with the actual accuracy (Table 12). The Expected Calibration Error (ECE) is the weighted average of the gap between the two,

$$\mathrm{ECE} = \sum_{b=1}^{B} \frac{n_b}{n} \left| \mathrm{acc}(b) - \mathrm{conf}(b) \right|$$

The ECE of the final model is 0.0259, and its mean confidence (0.9334) is 1.9 percentage points above its accuracy (0.9148).

![Figure 9: Reliability diagram of the final model on the test set. The dashed line is perfect calibration; bars below it indicate overconfidence.](../run_448px_binary/figures/reliability_diagram.png)

The bins show a mixed picture: the 0.5-0.6 bin is under-confident (accuracy 0.648 against confidence 0.547), while the bins from 0.6 to 1.0 are all over-confident, and the largest bin (0.9-1.0, 1,173 images) has an accuracy of 0.975 against a confidence of 0.987. The ECE is small, but 29 of the 128 wrong predictions (23%) were made with more than 90% confidence, the same pattern as the three melanomas in Section 2.16.

**Table 12. Reliability table of the final model on the test set.**

| Confidence bin | Images | Mean confidence | Accuracy |
|:---------------|-------:|----------------:|---------:|
| 0.5-0.6 | 54 | 0.547 | 0.648 |
| 0.6-0.7 | 54 | 0.648 | 0.574 |
| 0.7-0.8 | 92 | 0.751 | 0.652 |
| 0.8-0.9 | 130 | 0.858 | 0.808 |
| 0.9-1.0 | 1,173 | 0.987 | 0.975 |
| All | 1,503 | 0.933 | 0.915 |

Common fixes for overconfidence [10] are temperature scaling (dividing the logits by a constant fitted on the validation set), label smoothing and ensembles. This project already uses an ensemble, which usually improves calibration because averaging probabilities softens the extremes. A temperature could be fitted on the validation set without touching the test set, but it was not applied because it does not change the predicted class. For clinical use a calibrated probability matters: 0.99 should mean near certainty, and the results above show that this is not exactly true, so a deployed system should report the calibrated value and abstain when the probability is in the uncertain range.

## References

[1] A. Kolesnikov et al., "Big Transfer (BiT): General visual representation learning," in Proc. Eur. Conf. Comput. Vis. (ECCV), 2020, pp. 491–507.

[2] M. Abadi et al., "TensorFlow: A system for large-scale machine learning," in Proc. USENIX Symp. Oper. Syst. Des. Implement. (OSDI), 2016, pp. 265–283.

[3] P. Tschandl, C. Rosendahl, and H. Kittler, "The HAM10000 dataset, a large collection of multi-source dermatoscopic images of common pigmented skin lesions," Sci. Data, vol. 5, no. 1, Art. no. 180161, 2018.

[4] N. C. F. Codella et al., "Skin lesion analysis toward melanoma detection: A challenge at the 2017 International Symposium on Biomedical Imaging (ISBI), hosted by the International Skin Imaging Collaboration (ISIC)," in Proc. IEEE Int. Symp. Biomed. Imaging (ISBI), 2018, pp. 168–172.

[5] M. Combalia et al., "Validation of artificial intelligence prediction models for skin cancer diagnosis using dermoscopy images: the 2019 International Skin Imaging Collaboration Grand Challenge," Lancet Digit. Health, vol. 4, no. 5, pp. e330–e339, 2022.

[6] C. Hernández-Pérez et al., "BCN20000: Dermoscopic lesions in the wild," Sci. Data, vol. 11, no. 1, Art. no. 641, 2024.

[7] K. He, X. Zhang, S. Ren, and J. Sun, "Deep residual learning for image recognition," in Proc. IEEE Conf. Comput. Vis. Pattern Recognit. (CVPR), 2016, pp. 770–778.

[8] D. P. Kingma and J. Ba, "Adam: A method for stochastic optimization," in Proc. Int. Conf. Learn. Represent. (ICLR), 2015.

[9] H. Touvron, A. Vedaldi, M. Douze, and H. Jégou, "Fixing the train-test resolution discrepancy," in Proc. Adv. Neural Inf. Process. Syst. (NeurIPS), 2019.

[10] C. Guo, G. Pleiss, Y. Sun, and K. Q. Weinberger, "On calibration of modern neural networks," in Proc. Int. Conf. Mach. Learn. (ICML), 2017, pp. 1321–1330.
