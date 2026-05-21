import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn import metrics

def confusion_matrix(y_test, y_pred):
    # Compare real and modeled outcomes with confusion matrix
    fig, ax = plt.subplots()
    cnf_matrix = metrics.confusion_matrix(y_test, y_pred)
    labels = np.array([
        ['\n\nTrue Negatives\n(Non-Evictions We Predicted)', '\n\nFalse Positives\n(Non-Evictions We Missed)'],
        ['\n\nFalse Negatives\n(Evictions We Missed)', '\n\nTrue Positives\n(Evictions We Predicted)']])
    # labels = np.char.add('\n', labels)
    annot = np.char.add(cnf_matrix.astype(str), labels)
    sns.heatmap(pd.DataFrame(cnf_matrix), annot=annot, cmap="YlGnBu" ,fmt='', cbar=False, yticklabels=['Not Evicted (0)','Evicted (1)'], xticklabels=['Not Evicted (0)','Evicted (1)'])
    ax.xaxis.set_label_position("top")
    plt.tight_layout()
    plt.title('Confusion matrix', y=1.1)
    plt.ylabel('Actual')
    plt.xlabel('Predicted')
    plt.show()

def predict_with_threshold(model, X_test, threshold=0.5):
    y_pred_proba = model.predict_proba(X_test)[:,1]
    return (y_pred_proba > threshold).astype(int)

def plot_fit_stats(model, X_test, y_test):
    thresholds = np.arange(0.0, 1.1, 0.1)
    accuracies = []
    precisions = []
    recalls = []
    for threshold in thresholds:
        y_pred = predict_with_threshold(model, X_test, threshold)
        accuracies.append(metrics.accuracy_score(y_test, y_pred))
        precisions.append(metrics.precision_score(y_test, y_pred, zero_division=0))
        recalls.append(metrics.recall_score(y_test, y_pred, zero_division=0))
    df = pd.DataFrame({
        'threshold': thresholds,
        'accuracy': accuracies,
        'precision': precisions,
        'recall': recalls,
    })
    ax = df.plot('threshold', 'accuracy')
    df.plot('threshold', 'precision', ax=ax)
    df.plot('threshold', 'recall', ax=ax)

def roc_plot(model, y_test, X_test):
    y_pred_proba = model.predict_proba(X_test)[:,1]
    # y_pred_proba = predict_prop(model, X_test)
    fpr, tpr, _ = metrics.roc_curve(y_test,  y_pred_proba)
    auc = metrics.roc_auc_score(y_test, y_pred_proba)
    plt.plot(fpr,tpr,label="ROC, AUC="+str(round(auc, 2)))
    plt.legend(loc=4)
    plt.xlabel("False Positive Rate (1 - Specificity)")
    plt.ylabel("True Positive Rate (Sensitivity)")
    plt.show()