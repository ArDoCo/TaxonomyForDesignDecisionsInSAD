from enum import Enum
from anytree import Node, RenderTree, find_by_attr
import nltk
from nltk.tokenize import RegexpTokenizer, word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords, wordnet
from nltk.tag import pos_tag
import re
import pandas as pd
import numpy as np
from prettytable import PrettyTable


class LevelOfClassification(Enum):
    """
    With the different levels of classification, you can define the classes from the classification scheme you want to
    use as labels. If you mention classes having children nodes here, those children nodes will be combined in the root
    class.
    """
    LEVEL_0 = ['design decision']
    LEVEL_1 = ['existence decision', 'property decision', 'executive decision']
    LEVEL_2 = ['structural decision', 'behavioral decision', 'arrangement decision']
    LEAVES = ['integration', 'data file', 'interface', 'component', 'association', 'class', 'inheritance', 'architectural style',
             'architectural pattern', 'reference architecture', 'relation', 'function', 'algorithm', 'messaging', 'guideline',
             'design rule', 'organizational/process-related', 'tool', 'data base', 'platform', 'user interface', 'api', 'programming language', 'framework']


class Config(dict):
    """
    Config saves a configuration for the classification process with key value pairs.
    """
    def __init__(self, **kwargs):
        """
        Constructor method sets up a new configuration. All key value pairs given as parameters will be saved as
        attributes.
        :param kwargs: key value pair
        """
        super().__init__(**kwargs)
        for k, v in kwargs.items():
            setattr(self, k, v)

    def set(self, key, val):
        """
        Update or create a new key value pair in the configuration.
        :param key: reference to find pair again
        :param val: value (configuration)
        """
        self[key] = val
        setattr(self, key, val)


class TextPreprocessor:
    """
    TextPreprocessor provides functionality to preprocess text (sentences, text documents etc.) with different
    preprocessing, namely removing special characters and digits, do lowercasing, removing stop words and do stemming
    and lemmatisation.
    """
    def __init__(self):
        """
        Constructor for a TextProprocessor. To initialize the preprocessor, vocabulary und tokens from NLTK will be
        downloaded.
        """
        nltk.download('wordnet')
        nltk.download('punkt')
        nltk.download('stopwords')

    def preprocess(self, sentence: str, do_cleanup=False, do_lowercasing=False, do_stop_word_removal=False,
                   do_lemmatization=False):
        """
        Functionality to transform a given sentence with different preprocessing techniques, depending on the given
        configuration in the parameters. The default configuration sets every technique to false.
        :param sentence: input which will be transformed with given techniques
        :param do_cleanup: if set to true, special characters, digits and hyperlinks will be removed
        :param do_lowercasing: if set to true, all characters will be lowercased
        :param do_stop_word_removal: if set to true, stop words from NLKT.corpus.stopwords will be removed
        :param do_lemmatization: if set to true, words will be reduced to their lemma
        :return: sentence after applying the preprocessing techniques

        See: https://stackoverflow.com/a/54398984
        """
        sentence = str(sentence)
        if do_lowercasing:
            sentence = sentence.lower()
        if do_cleanup:
            sentence = sentence.replace('{html}', "")
            cleanr = re.compile('<.*?>')
            cleantext = re.sub(cleanr, '', sentence)
            rem_url = re.sub(r'http\S+', '', cleantext)
            rem_num = re.sub('[0-9]+', '', rem_url)
            tokenizer = RegexpTokenizer(r'\w+')
            tokens = tokenizer.tokenize(rem_num)
        else:
            tokens = word_tokenize(sentence)

        if do_stop_word_removal:
            filtered_words = [w for w in tokens if not w in stopwords.words('english')]
        else:
            filtered_words = [w for w in tokens]
        
        if do_lemmatization:
            pos_tags=pos_tag(filtered_words)
            lemmatizer = WordNetLemmatizer()
            lemma_words = [lemmatizer.lemmatize(w,self.get_wordnet_pos(pos_tag)) for (w,pos_tag) in pos_tags]

        else:
            lemma_words = filtered_words

        return " ".join(lemma_words)

    
    def get_wordnet_pos(self,treebank_tag):
        """
        Use this method to convert treebank POS tag to WordNet format
        param treebank_tag: Penn Treebank POS tag to convert
        :return: POS tag in wordnet format
        """
        if treebank_tag.startswith('J'):
            return wordnet.ADJ
        elif treebank_tag.startswith('V'):
            return wordnet.VERB
        elif treebank_tag.startswith('N'):
            return wordnet.NOUN
        elif treebank_tag.startswith('R'):
            return wordnet.ADV
        else:
            # Use noun as default
            return wordnet.NOUN



class LabelPreprocessor:
    """
    LabelPreprocessor provides functionality to preprocess labels in a pandas.DataFrame. For different learning
    algorithms and the use of machine learning libraries specific labelling is necessary, e.g. integer labels.
    """
    def __init__(self):
        """
        Default constructor for LabelPreprocessor. LabelPreprocessor objects can be used preprocess labels from a
        pandas.DataFrame.
        """
        pass

    def transform_df_unified_labels(self, df: pd.DataFrame, column_name: str, classification_scheme: Node,
                                    level_of_classification: LevelOfClassification, label_unrelated: str):
        """
        Use this method to transform the labels present in column with 'column_name' in Dataframe 'df' to a label which
        fits the classes on the selected 'level_of_classification' using the given 'classification_scheme'.
        Labels must be transformed if one does not want to apply the classification scheme as a whole but wants to focus
        on specific classes, which can be defined in enumeration LevelOfClassification.
        :param df: The pandas.DataFrame in which one column with labels should be transformed.
        :param column_name: The name of the column in df which specifies the labels.
        :param classification_scheme: Root node of the classification scheme (e.g. 'design decision') which is starting
                point for traversal
        :param level_of_classification: Element from enumeration LevelOfClassification which defines target labels.
        :param label_unrelated: Name for all items that do not fit any class on the selected level of classification.
        :return: Transformed corpus where labels are in given column are only from given level or label_unrelated
        """
        corpus_transformed = df.copy()
        for index, row in corpus_transformed.iterrows():
            row[column_name] = self.__adjust_label(classification_scheme, level_of_classification, row[column_name],
                                                   label_unrelated)
        return corpus_transformed

    def generate_dictionary_for_integer_labels(self, categories, label_unrelated):
        """
        For learning algorithms, sometimes integer labels must be provided. Therefore, use this method to create a
        dictionary which maps a category to a integer (equal to its index in 'categories' + 1). 'label_unrelated' will
        always be mapped to 0.
        :param categories: Iterable data structure which lists all categories/ labels.
        :param label_unrelated: Name for the class which sums up all unrelated data points.
        :return: A dictionary which provides a matching between each class from 'categories' plus 'label_unrelated' with
                    integer values. The integer values should be used as labels.
        """
        categories_with_integer_labels = dict()
        categories_with_integer_labels[label_unrelated] = 0
        for category in categories:
            categories_with_integer_labels[category] = categories.index(category) + 1
        return categories_with_integer_labels

    def transform_df_integer_labels(self, df: pd.DataFrame, column_name: str, dictionary_for_integer_labels: dict):
        """
        Transform every value in column with 'column_name' in pandas.DataFrame 'df' to a integer label. Integer labels
        can better be used as input in machine learning algorithms. The integer labels are generated by replacing every
        string given as key in 'dictionary_for_integer_labels' by the corresponding value in
        'dictionary_for_integer_labels'.
        :param df: The pandas.DataFrame in which one column with labels should be transformed.
        :param column_name: The name of the column in 'df' where labels should be replaced with integer values.
        :param dictionary_for_integer_labels: Matching between a textual label with a corresponding integer value.
        :return: Transformed DataFrame where each value from original DataFrame 'df' column 'column_name' is replaced
                    with integer value if a mapping in the dictionary exists.
        """
        df_with_integer_values = df.copy()
        for index, row in df_with_integer_values.iterrows():
            for label in dictionary_for_integer_labels:
                if row[column_name] == label:
                    row[column_name] = dictionary_for_integer_labels.get(label)
        return df_with_integer_values

    def transform_df_multi_label(self, df: pd.DataFrame, first_column_name: str, second_column_name: str,
                                 new_column_name: str, value_unrelated=0):
        """
        This combines the labels in the two columns 'first_column_name' and 'second_column_name' in pandas.DataFrame
        'df' to a multi label. A multi label is represented by an array of values, which includes all unique labels in
        the row of the original data frame. On this, one can perform sklearn.MultiLabelBinarizer.fit_transform().
        :param df: The pandas.DataFrame in which one column with labels should be transformed.
        :param first_column_name: Extract labels from the first column and combine them to multi label.
        :param second_column_name: Extract labels from the second column and combine them to multi label.
        :param new_column_name: Name for the column with multi labels in target data frame.
        :param value_unrelated: Index of class 'unrelated' so that this is not included in the multi label if it is only
                present in the second column (do not override first column).
        :return: pandas.DataFrame which is equal to 'df' and has another column with 'column_name' which provides
                    vectors for multi label classification.
        """
        corpus_multi_label = df.copy()
        corpus_multi_label[new_column_name] = ""
        for index, row in corpus_multi_label.iterrows():
            multi_label = []
            multi_label.append(row[first_column_name])
            if row[second_column_name] != value_unrelated and row[second_column_name] != row[first_column_name]:
                multi_label.append(row[second_column_name])

            row[new_column_name] = multi_label
        return corpus_multi_label

    def __get_classes_on_classification_level(self, classification_scheme: Node,
                                              level_of_classification: LevelOfClassification):
        """
        Search for representation of the classes given in 'level_of_classification' in the 'classification_scheme'.
        This transfers the string to a node representation.
        :param classification_scheme: Root node of hierarchical scheme.
        :param level_of_classification: Selection of enumeration LevelOfClassification representing the names of the
                selected classes.
        :return: A list of nodes taken from the classification scheme. Each node is the representation of one of the
                 classes mentioned in 'level_of_classification'.
        """
        class_names = level_of_classification.value
        nodes = []
        for selected_class in class_names:
            node_for_selected_class = find_by_attr(classification_scheme, selected_class)
            nodes.append(node_for_selected_class)
        return nodes

    def __adjust_label(self, classification_scheme: Node, level_of_classification: LevelOfClassification,
                       label: str, label_unrelated: str):
        """
        Returns the label itself if it is one of the classes on the selected 'level_of_classification' or a label for a
        class which is above in hierarchy and given in 'level_of_classification'. If none fits, it
        returns 'label_unrelated'.
        :param classification_scheme: Root node of hierarchical scheme.
        :param level_of_classification: Selection of enumeration LevelOfClassification representing the names of the
                selected classes.
        :param label: Original label.
        :param label_unrelated: Label which should be used if none from the scheme fits.
        :return: Adjusted label which either fits the class or its parent class or the 'label_unrelated'.
        """
        nodes = self.__get_classes_on_classification_level(classification_scheme, level_of_classification)
        for node in nodes:
            if label == node.name or label in self.__get_list_of_children_in_scheme(node):
                return node.name
        return label_unrelated

    def __get_list_of_children_in_scheme(self, root_node: Node):
        """
        Search method for schemes using library anytree. It returns a list of all children for the given root node.
        :param root_node: Starting point for traversal (anytree.Node).
        :return: List of children (list of anytree.Node).
        """
        result = []
        queue = []
        for child in root_node.children:
            queue.append(child)
        while queue:
            current = queue[0]
            result.append(current.name)
            for child in current.children:
                queue.append(child)
            queue.pop(0)
        return result


class ResultPresenter:
    """
    ResultPresenter provides functionality for transforming results from machine learning processes into a well-formed
    presentation. Using this, scores can be printed in good looking tables and average can be calculated.
    """
    def __init__(self):
        """
        Create an instance of ResultPresenter.
        """
        pass

    def calculate_average_over_matrix(self, matrix, decimal_places=4):
        """
        Calculate und return the average over all values in the 2D matrix.
        :param matrix: Scoring matrix.
        :param decimal_places: Number of digits behind comma (function performs round operation).
        :return: Average over all values in the matrix.
        """
        average = 0
        for row in matrix:
            for item in row:
                average += item
        average /= len(matrix) * len(matrix[0])
        average = round(average, decimal_places)
        return average

    def present_results_in_table(self, table_name, classifiers, vectorizers, scores, decimal_places=4):
        """
        Specific method for the evaluation of classifiers in combination with vectorizers. The results in the table
        represent the scores with correct row and column names, which are the classifiers (rows) and columns
        (vectorizers).
        :param table_name: Option to give the returned table a name, which will be written in upper-left field.
        :param classifiers: List of all evaluated classifiers.
        :param vectorizers: List of all evaluated vectorizers.
        :param scores: Scoring matrix (2D).
        :param decimal_places: Number of digits behind comma (function performs round operation).
        :return: A prettytable.PrettyTable which can be used to print the results in a good looking way.
        """
        scores_rounded = scores.copy()
        for i in range(0, len(classifiers)):
            for j in range(0, len(vectorizers)):
                scores_rounded[i][j] = round(scores_rounded[i][j], 4)

        result_table = PrettyTable()
        column_names = [type(vectorizers[j]).__name__ + " " + str(vectorizers[j].ngram_range) for j in
                        range(0, len(vectorizers))]
        column_names.insert(0, table_name)

        result_table.field_names = column_names
        for i in range(0, len(classifiers)):
            classifier_name = [type(classifiers[i]).__name__]
            row_value = classifier_name + scores_rounded[i]
            result_table.add_row(row_value)

        return result_table
