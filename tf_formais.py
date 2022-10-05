import itertools
from pythomata import SimpleDFA
import pathlib

#Função principal
def main():
    # Lê o arquivo de entrada com a linguagem
    print("Digite o nome do arquivo de entrada da linguagem sem sua extensão:\n")
    languageFileName = input()
    #languageFileName = "00_aut_trabalho"    # Nome da entrada
    
    #=========================================================
    # CONVERSÃO DO INPUT EM .TXT
    #=========================================================
    # Traduz o input para uma classe
    inputLines = readTxtFile(languageFileName)                                      # Linhas do .txt da entrada
    translatedInput = InputTranslation(inputLines)                                  # Classe com todas informações do input

    # Cria o autômato e printa uma imagem dele
    automata = FiniteAutomata(translatedInput)                                      # Classe de autômato finito
    automata.printAutomata("00 - autômato fornecido")
    #=========================================================
    # CHECAGEM DE LINGUAGEM VAZIA
    #=========================================================
    if automata.isLanguageEmpty():
        print("A linguagem fornecida é vazia\n")
        return
    
    print("A linguagem fornecida não é vazia\n")
    #=========================================================
    print("\nVocê deseja remover os estados inalcançáveis? [s/n]:")
    removeUnreachableStates = input()

    if removeUnreachableStates == "s":
        automata.removeUnreachableStates()
        automata.printAutomata("02 - autômato sem estados inúteis")
    #=========================================================
    print("\nVocê deseja criar uma função total? [s/n]:")
    createTotalFunction = input()

    if createTotalFunction == "s":
        automata.createTotalFunctionIfNot()
        automata.printAutomata("03 - autômato com função total")
    #=========================================================
    # COMEÇO DA MINIMIZAÇÃO
    #=========================================================
    print("\nVocê deseja fazer a equivalência entre estados? [s/n]:")
    makeEquivalence = input()

    if makeEquivalence == "s":
        automata.verifyEquivalenceBetweenPairs()
    #=========================================================
    print("\nVocê deseja criar agrupar dois estados equivalentes? [s/n]:")
    grouptTwoStates = input()

    if grouptTwoStates == "s":
        print("Digite o nome dos dois estados separados por uma vírgula:\n")
        statesNames = input().split(",")
        automata.unifyTwoStates(automata.statesDictionary[statesNames[0]], automata.statesDictionary[statesNames[1]])
        #automata.verifyEquivalenceBetweenPairs()
        automata.printAutomata("04 - autômato com estados equivalentes agrupados")
    #=========================================================
    print("\nVocê deseja remover os estados inalcançáveis novamente? [s/n]:")
    removeUnreachableStatesAgain = input()

    if removeUnreachableStatesAgain == "s":
        automata.removeUnreachableStates()
        automata.printAutomata("05 - autômato sem minimizado")
    #=========================================================
    # CHECAGEM DE INPUT DE PALAVRAS
    #=========================================================
    print("Você deseja checar uma lista de palavras? [s/n]:\n")
    checkWords = input()

    if checkWords == "s":
        print("\nDigite o nome do arquivo de entrada das palavras sem sua extensão:")
        wordsFileName = input()
        #wordsFileName = "palavras"
        automata.checkAcceptanceOfInputWords(wordsFileName)


def readTxtFile(name):
    with open(name + ".txt") as input:
        inputLines = input.readlines()

    return inputLines

class InputTranslation:                                     # Classe que traduz o input para dados do programa
    def __init__(self, inputLines):
        self.name = self.extractNameFromInput(inputLines)
        self.alphabet = self.extractAlphabetFromInput(inputLines)
        self.initialState = self.extractInitialStateFromInput(inputLines)
        self.finalStates = self.extractFinalStatesFromInput(inputLines)
        self.states = self.extractStatesFromInput(inputLines)
        self.transitions = self.extractTransistionsFromInput(inputLines)

    def extractNameFromInput(self, inputLines):             # Extrai o nome do input
        nameIndex = 0
        name = inputLines[nameIndex]

        return name

    def extractAlphabetFromInput(self, inputLines):         # Extrai o alfabeto do input
        alphabetIndex = 2
        unprocessedAlphabetWithTitle = inputLines[alphabetIndex]
        unprocessedAlphabet = unprocessedAlphabetWithTitle[3:].strip()
        alphabet = unprocessedAlphabet.split(",")

        return alphabet

    def extractInitialStateFromInput(self, inputLines):     # Extrai o estado inicial do input
        initialStateIndex = 3
        unprocessedInitialStateWithTitle = inputLines[initialStateIndex]
        unprocessedInitialState = unprocessedInitialStateWithTitle[3:]
        initialState = unprocessedInitialState.strip()

        return initialState

    def extractFinalStatesFromInput(self, inputLines):      # Extrai o estado final do input
        finalStateIndex = 4
        unprocessedFinalStateWithTitle = inputLines[finalStateIndex]
        unprocessedFinalState = unprocessedFinalStateWithTitle[3:].strip()
        finalState = unprocessedFinalState.split(",")

        if not isinstance(finalState, list):
            finalState = [finalState]

        return finalState

    def extractStatesFromInput(self, inputLines):           # Extrai todos os estados do input
        statesIndex = 1
        unprocessedStatesWithTitle = inputLines[statesIndex]
        unprocessedStates = unprocessedStatesWithTitle[3:].strip()
        states = unprocessedStates.split(",")

        if not isinstance(states, list):
            states = [states]

        return states

    def extractTransistionsFromInput(self, inputLines):     # Extrai as transições do input
        transitionsStartIndex = 6
        unprocessedTransitions = inputLines[transitionsStartIndex:]
        transitions = []

        for unprocessedTransition in unprocessedTransitions:
            transition = unprocessedTransition[1:-1]

            if transition[-1] == ")":
                transition = transition[:-1]

            transitions.append(transition.split(","))

        return transitions

class State:                                                # Classe de estado
    def __init__(self, name):
        self.name = name                                    # Nome
        self.transitionsPointingIn = []                     # Transições que estão apontando para este estado
        self.transitionsPointingOut = []                    # Transições que estão apontando a partir deste estado
        self.isFinalState = False
        self.isInitialState = False
    
    def __eq__(self, other):                                # Verifica a igualdade entre dois estados pelo nome
        return self.name == other.name

class Transition:                                           # Classe de transição
    def __init__(self, transitionData, statesDictionary):
        fromState = statesDictionary[transitionData[0]]
        fromState.transitionsPointingOut.append(self)
        self.pointsFrom = fromState                                                 # Estado onde a transição começa

        toState = statesDictionary[transitionData[2]]
        toState.transitionsPointingIn.append(self)
        self.pointsTo = toState                                                     # Estado onde a transição termina

        self.name = self.pointsFrom.name + "To" + self.pointsTo.name                # Nome único da transição
        self.acceptedSymbols = set()                                                # Todos os símbolos que fazem com que essa transição passe de um estado para o outro
        self.isLoop = self.checkIfItIsInternalLoop(self.pointsFrom, self.pointsTo)  # Verifica se a transição é um loop próprio em um estado


    def checkIfItIsInternalLoop(self, pointsFrom, pointsTo):
        if pointsFrom.name == pointsTo.name:
            return True
        
        return False

class FiniteAutomata:
    def __init__(self, translatedInput):
        self.name = translatedInput.name
        self.alphabet = translatedInput.alphabet

        self.statesNames = translatedInput.states
        self.statesDictionary = self.createStatesDictionary(self.statesNames)

        self.initialStateName = translatedInput.initialState
        self.setInitialState(self.initialStateName)

        self.finalStateNames = translatedInput.finalStates
        self.setFinalStates(self.finalStateNames)

        self.transitionsList = translatedInput.transitions
        self.transitionsDictionary = self.createTransitionsDictionary(self.transitionsList)
        self.transitionKeys = self.transitionsDictionary.keys()

    
    def createStatesDictionary(self, statesNames):
        statesDictionary = {}

        for stateName in statesNames:
            state = State(stateName)
            statesDictionary[stateName] = state

        return statesDictionary

    def createTransitionsDictionary(self, transitionsList):
        transitionsDictionary = {}

        for transitionData in transitionsList:
            transitionKey = transitionData[0] + "To" + transitionData[2]

            if not transitionKey in transitionsDictionary:
                newTransition = Transition(transitionData, self.statesDictionary)
                transitionsDictionary[transitionKey] = newTransition

            transitionsDictionary[transitionKey].acceptedSymbols.add(transitionData[1])

        return transitionsDictionary

    def setInitialState(self, initialStateName):
        state = self.statesDictionary[initialStateName]
        state.isInitialState = True

    def setFinalStates(self, finalStateNames):
        for finalStateName in finalStateNames:
            state = self.statesDictionary[finalStateName]
            state.isFinalState = True
    

    #Gera uma imagem do resultado
    def printAutomata(self, name):
        pythomata = self.convertToPythomata()
        currentPath = pathlib.Path(__file__).parent.resolve()
        graph = pythomata.to_graphviz()
        graph.filename = name
        graph.format = "png"
        graph.render(directory=currentPath, view=True)

    def convertToPythomata(self):
        alphabet = set(self.alphabet)
        states = set(self.statesNames)
        initial_state = self.initialStateName
        accepting_states = set(self.finalStateNames)

        transition_function = dict()
        for state in self.statesDictionary.values():
            transitionsDictionary = dict()
            for transition in state.transitionsPointingOut:
                for symbol in transition.acceptedSymbols:
                    transitionsDictionary[symbol] = transition.pointsTo.name
            transition_function[state.name] = transitionsDictionary
            
        dfa = SimpleDFA(states, alphabet, initial_state, accepting_states, transition_function)

        return dfa
    
    # Verifica se existe um caminho entre o estado inicial e o estado final
    def isLanguageEmpty(self):
        initialState = self.statesDictionary[self.initialStateName]
        visitedStatesFromInitial = set()
        self.getReachableStatesRecursion(initialState, visitedStatesFromInitial)

        for stateName in visitedStatesFromInitial:
            state = self.statesDictionary[stateName]

            if state.isFinalState:
                return False

        return True

    #Minimização do autômato
    def minimize(self):
        self.removeUnreachableStates()          # Eliminação de estados inúteis
        self.createTotalFunctionIfNot()         # Criação da função total
        self.unifyEquivalentStates()            # Unificação de estados equivalentes
        self.removeUnreachableStates()          # Eliminação de estados inúteis


    #Eliminação de estados inúteis
    def removeUnreachableStates(self):                                      # Remove os estados inúteis
        unreachableStateNames = self.getUnreachableStateNamesSet()

        for unreachableStateName in unreachableStateNames:
            self.deleteStateByName(unreachableStateName)

    def deleteStateByName(self, stateName):                                 # Deleta um estado, dado seu nome
        state = self.statesDictionary[stateName]

        for transition in state.transitionsPointingIn:
            stateToChange = transition.pointsFrom
            listOfTransitionsToCheck = stateToChange.transitionsPointingOut

            indexToRemove = 0
            for i, transitionToCheck in enumerate(listOfTransitionsToCheck):
                if transitionToCheck.name == transition.name:
                    indexToRemove = i
                    break
            
            stateToChange.transitionsPointingOut.pop(indexToRemove)

            self.transitionsDictionary.pop(transition.name)

        for transition in state.transitionsPointingOut:
            stateToChange = transition.pointsTo
            listOfTransitionsToCheck = stateToChange.transitionsPointingIn

            indexToRemove = 0
            for i, transitionToCheck in enumerate(listOfTransitionsToCheck):
                if transitionToCheck.name == transition.name:
                    indexToRemove = i
                    break
            
            stateToChange.transitionsPointingIn.pop(indexToRemove)

            self.transitionsDictionary.pop(transition.name)
        
        self.transitionKeys = self.transitionsDictionary.keys()

        self.statesNames.remove(state.name)
        self.statesDictionary.pop(state.name)

        if state.isInitialState:
            if self.initialStateName == state.name:
                self.initialStateName = None

        if state.isFinalState:
            self.finalStateNames.remove(state.name)

    def getUnreachableStateNamesSet(self):                                  # Através da intersecção entre todos estados e os estados úteis, descobre os estados inúteis
        initialState = self.statesDictionary[self.initialStateName]
        finalStates = []

        for finalStateName in self.finalStateNames:
            finalStates.append(self.statesDictionary[finalStateName])

        reachableStatesSet = self.getReachableStateNamesSet(initialState, finalStates)
        allStates = self.statesNames
        unreachableStateNames = set(allStates).difference(reachableStatesSet)

        return unreachableStateNames

    def getReachableStateNamesSet(self, initialState, finalStates):         # Verifica através de uma recursão DFS quais são os estados úteis
        visitedStatesFromInitial = set()
        visitedStatesFromFinalStates = set()
        self.getReachableStatesRecursion(initialState, visitedStatesFromInitial)

        for finalState in finalStates:
            if finalState.name not in visitedStatesFromFinalStates:
                self.getStatesThatReachRecursion(finalState, visitedStatesFromFinalStates)

        reachableStates = visitedStatesFromInitial.intersection(visitedStatesFromFinalStates)
        return reachableStates

    def getReachableStatesRecursion(self, state, visitedStates):            # Recursão que verifica quais estados são atingíveis a partir de um estado
        # Mark the current node as visited and print it
        visitedStates.add(state.name)

        reachableStateNames = []
        for transition in state.transitionsPointingOut:
            if transition.pointsTo.name not in reachableStateNames and transition.pointsTo.name != state.name:
                reachableStateNames.append(transition.pointsTo.name)
        
        reachableStates = []
        for reachableStateName in reachableStateNames:
            reachableStates.append(self.statesDictionary[reachableStateName])

        for reachableState in reachableStates:
            if reachableState.name not in visitedStates:
                self.getReachableStatesRecursion(reachableState, visitedStates)

    def getStatesThatReachRecursion(self, state, visitedStates):            # Recursão que verifica quais estados chegam a um outro estado
        visitedStates.add(state.name)

        reachableStateNames = []
        for transition in state.transitionsPointingIn:
            if transition.pointsFrom.name not in reachableStateNames and transition.pointsFrom.name != state.name:
                reachableStateNames.append(transition.pointsFrom.name)
        
        reachableStates = []
        for reachableStateName in reachableStateNames:
            reachableStates.append(self.statesDictionary[reachableStateName])

        for reachableState in reachableStates:
            if reachableState.name not in visitedStates:
                self.getStatesThatReachRecursion(reachableState, visitedStates)


    #Criação da função total
    def createTotalFunctionIfNot(self):                                     # Cria uma função total no autômato
        listOfTransitionsToCreate = self.getMissingSymbolsToTotalFunction()

        if len(listOfTransitionsToCreate) != 0:
            dummyState = State("dummy")
            self.statesDictionary[dummyState.name] = dummyState
            self.statesNames.append(dummyState.name)

            for transitionToCreate in listOfTransitionsToCreate:
                state = transitionToCreate[0]
                missingTransitionSymbols = transitionToCreate[1]
                transitionData = [state.name, [], dummyState.name]
                newTransition = Transition(transitionData, self.statesDictionary)
                newTransition.acceptedSymbols.update(missingTransitionSymbols)
                transitionKey = transitionData[0] + "To" + transitionData[2]
                self.transitionsDictionary[transitionKey] = newTransition

    def getMissingSymbolsToTotalFunction(self):                             # Verifica os símbolos faltantes em cada estado para formar uma função total
        alphabetSet = set(self.alphabet)
        listOfTransitionsToCreate = []

        for state in self.statesDictionary.values():
            if state.isFinalState:
                continue

            stateTransitionsPointingOutSymbols = set()

            for transition in state.transitionsPointingOut:
                stateTransitionsPointingOutSymbols.update(set(transition.acceptedSymbols))
            
            missingTransitionSymbols = alphabetSet.difference(stateTransitionsPointingOutSymbols)

            if len(missingTransitionSymbols) != 0:
                listOfTransitionsToCreate.append([state, missingTransitionSymbols])

        return listOfTransitionsToCreate
    

    #Verificação de estados equivalentes
    def verifyEquivalenceBetweenPairs(self):
        finalStates = self.getFinalStates()
        nonFinalStates = self.getNonFinalStates()
        finalStatesPairs = list(itertools.combinations(finalStates, 2))
        nonFinalStatesPairs = list(itertools.combinations(nonFinalStates, 2))

        equivalentPairs = []
        notEquivalentPairs = []
        possiblyEquivalentFinalStatePairs = []
        possiblyEquivalentNonFinalStatePairs = []


        for finalStatesPair in finalStatesPairs:
            if self.areTwoStatesEquivalent(finalStatesPair[0], finalStatesPair[1], equivalentPairs, notEquivalentPairs):
                possiblyEquivalentFinalStatePairs.append(finalStatesPair)

        print("\nEstados finais com possível equivalência\n")
        for possiblyEquivalentFinalStatePair in possiblyEquivalentFinalStatePairs:
            print(possiblyEquivalentFinalStatePair[0].name + " -> " + possiblyEquivalentFinalStatePair[1].name)
        

        for nonFinalStatesPair in nonFinalStatesPairs:
            if self.areTwoStatesEquivalent(nonFinalStatesPair[0], nonFinalStatesPair[1], equivalentPairs, notEquivalentPairs):
                possiblyEquivalentNonFinalStatePairs.append(nonFinalStatesPair)

        print("\nEstados não-finais com possível equivalência\n")
        for possiblyEquivalentNonFinalStatePair in possiblyEquivalentNonFinalStatePairs:
            print(possiblyEquivalentNonFinalStatePair[0].name + " -> " + possiblyEquivalentNonFinalStatePair[1].name)

    def getFinalStates(self):
        finalStates = []
        for finalStateName in self.finalStateNames:
            finalStates.append(self.statesDictionary[finalStateName])

        return finalStates

    def getNonFinalStates(self):
        nonFinalStatesNames = set(self.statesNames).difference(set(self.finalStateNames))
        nonFinalStates = []
        for nonFinalStatesName in nonFinalStatesNames:
            nonFinalStates.append(self.statesDictionary[nonFinalStatesName])

        return nonFinalStates

    def areTwoStatesEquivalent(self, firstState, secondState, equivalentPairs,notEquivalentPairs):              # Verifica se dois estados são equivalentes
        isEndOfPath = False
        for firstStateTransition in firstState.transitionsPointingOut:
            for firstStateTransitionSymbol in firstStateTransition.acceptedSymbols:
                for secondStateTransition in secondState.transitionsPointingOut:
                    for secondStateTransitionSymbol in secondStateTransition.acceptedSymbols:
                        if firstStateTransitionSymbol == secondStateTransitionSymbol:
                            statePointedByFirstTransition = firstStateTransition.pointsTo
                            statePointedBySecondTransition = secondStateTransition.pointsTo

                            if statePointedByFirstTransition.isFinalState or statePointedBySecondTransition.isFinalState:
                                isEndOfPath = True

                            if statePointedByFirstTransition.isFinalState != statePointedBySecondTransition.isFinalState:
                                if isEndOfPath:
                                    notEquivalentPairs.append([firstStateTransition.pointsFrom, secondStateTransition.pointsFrom])

                                return False
        if isEndOfPath:
            equivalentPairs.append([firstStateTransition.pointsFrom, secondStateTransition.pointsFrom])
        return True


    #Unifica dois estados 
    def unifyTwoStates(self, firstState, secondState):
        unifiedStateName = firstState.name + secondState.name
        unifiedState = State(unifiedStateName)

        if firstState.isInitialState or secondState.isInitialState:
            unifiedState.isInitialState = True
            self.initialStateName = unifiedState.name
        
        if firstState.isFinalState or secondState.isInitialState:
            unifiedState.isFinalState = True
            self.finalStateNames.append(unifiedState.name)

        self.statesDictionary[unifiedState.name] = unifiedState
        self.statesNames.append(unifiedState.name)

        self.unifyAllTransitionsPointingInForTwoStates(firstState, secondState, unifiedState)
        self.unifyAllTransitionsPointingOutForTwoStates(firstState, secondState, unifiedState)
        self.deleteStateByName(firstState.name)
        self.deleteStateByName(secondState.name)

    def unifyAllTransitionsPointingInForTwoStates(self, firstState, secondState, unifiedState):     # Junta todas transições que estão apontando para o estado unificado
        allTransitionsPointingIn = self.concatenateTransitionsOfTwoStates(firstState.transitionsPointingIn, secondState.transitionsPointingIn)
        
        transitionsDataToCreate = []
        for transition in allTransitionsPointingIn:
            newTransitionData = [transition.pointsFrom.name, transition.acceptedSymbols, unifiedState.name]
            transitionsDataToCreate.append(newTransitionData)

        for transitionData in transitionsDataToCreate:
            transitionKey = transitionData[0] + "To" + transitionData[2]

            if not transitionKey in self.transitionsDictionary:
                newTransition = Transition(transitionData, self.statesDictionary)
                self.transitionsDictionary[transitionKey] = newTransition

            self.transitionsDictionary[transitionKey].acceptedSymbols.update(transitionData[1])
    
    def unifyAllTransitionsPointingOutForTwoStates(self, firstState, secondState, unifiedState):    # Junta todas transições que estão apontando a partir do estado unificado
        allTransitionsPointingOut = self.concatenateTransitionsOfTwoStates(firstState.transitionsPointingOut, secondState.transitionsPointingOut)
        
        transitionsDataToCreate = []
        for transition in allTransitionsPointingOut:
            newTransitionData = [unifiedState.name, transition.acceptedSymbols, transition.pointsTo.name]
            transitionsDataToCreate.append(newTransitionData)

        for transitionData in transitionsDataToCreate:
            transitionKey = transitionData[0] + "To" + transitionData[2]

            if not transitionKey in self.transitionsDictionary:
                newTransition = Transition(transitionData, self.statesDictionary)
                self.transitionsDictionary[transitionKey] = newTransition

            self.transitionsDictionary[transitionKey].acceptedSymbols.update(transitionData[1])

    def concatenateTransitionsOfTwoStates(self, firstStateTransitions, secondStateTransitions):     # Junta todas transições de dois estados
        joinedTransitions = []

        for firstStateTransition in firstStateTransitions:
            joinedTransitions.append(firstStateTransition)

        for secondStateTransition in secondStateTransitions:
            joinedTransitions.append(secondStateTransition)
        
        return joinedTransitions


    #Verifica um input de palavras
    def checkAcceptanceOfInputWords(self, wordsFileName):                   # Checa a aceitação de um input em .txt
        inputLines = readTxtFile(wordsFileName)
        words = self.getWordsToTest(inputLines)
        acceptedAndRejectedList = []

        for i, word in enumerate(words):
            wordsAndStatus = []
            if self.isWordIsAccepted(word):
                wordAndStatus = [word, "ACCEPTED"]
            else:
                wordAndStatus = [word, "REJECTED"]

            acceptedAndRejectedList.append(wordAndStatus)

        self.writeOutputOnConsole(acceptedAndRejectedList)

        return acceptedAndRejectedList

    def getWordsToTest(self, inputLines):                                   # Pega as palavras do .txt
        words = []

        for line in inputLines:
            word = []
            for letter in line.strip():
                word.append(letter)
            
            words.append(word)

        return words
    
    def isWordIsAccepted(self, word):                                       # Verifica se uma palavra é aceita
        initialState = self.statesDictionary[self.initialStateName]
        actualState = initialState

        for letter in word:
            if len(actualState.transitionsPointingOut) == 0:
                return False

            for i, transition in enumerate(actualState.transitionsPointingOut):
                if letter in transition.acceptedSymbols:
                    actualState = transition.pointsTo
                    break
                
                if i == len(actualState.transitionsPointingOut) - 1:
                    return False

        if not actualState.isFinalState:
            return False

        return True

    def writeOutputOnConsole(self, acceptedAndRejectedList):                # Escreve o resultado das verificações no console
        for acceptedAndRejected in acceptedAndRejectedList:
            outputString = "".join(acceptedAndRejected[0]) + "  -->  " + acceptedAndRejected[1]
            print(outputString)


main()