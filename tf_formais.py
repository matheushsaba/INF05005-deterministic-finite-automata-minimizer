import itertools
from pythomata import SimpleDFA
import pathlib

#Função principal
def main():
    name = "Entradas_Formatadas_MatheusSabadin_GiuliaStefainski_EduardaWaechter"    # Nome da entrada
    inputLines = readTxtFile(name)                                                  # Linhas do .txt da entrada
    translatedInput = InputTranslation(inputLines)                                  # Classe com todas informações do input

    automata = FiniteAutomata(translatedInput)                                      # Classe de autômato finito
    automata.printAutomata("p1")

    automata.removeUnreachableStates()
    #automata.printAutomata("p2")

    initialState = automata.statesDictionary[automata.initialStateName]
    finalStates = []

    for finalStateName in automata.finalStateNames:
        finalStates.append(automata.statesDictionary[finalStateName])

    finalState = finalStates[0]

    #automata.printAllPaths(initialState, finalState)
    #automata.getEquivalentPairs()

    automata.createTotalFunctionIfNot()
    automata.printAutomata("p3")
    


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

class FiniteAutomataNx:
    def __init__(self, translatedInput):
        self.graph = nx.DiGraph()

        self.name = translatedInput.name
        self.alphabet = translatedInput.alphabet
        self.initialState = translatedInput.initialState
        self.finalStates = set(translatedInput.finalStates)

        self.createStateNodes(translatedInput)
        self.states = self.graph.nodes()

        self.createTransitions(translatedInput)
        self.transitions = self.graph.edges()

    
    def createStateNodes(self, translatedInput):
        for state in translatedInput.states:
            self.graph.add_node(state, isInitialState=self.isStateInitial(state), isFinalState=self.isStateFinal(state))

    def isStateInitial(self, state):
        if self.initialState == state:
            return True
        
        return False

    def isStateFinal(self, state):
        if state in self.finalStates:
            return True
        
        return False

    def createTransitions(self, translatedInput):
        for transition in translatedInput.transitions:
            self.graph.add_edge(transition[0], transition[2], label=transition[1])

    def drawAutomata(self):
        black = "#000000"
        white = "#FFFFFF"
        yellow = "#EADDCA"

        position=nx.spring_layout(self.graph)
        #Draws all the states
        nodes = nx.draw_networkx_nodes(self.graph, pos=position, node_size=800, node_color=black)
        nodes = nx.draw_networkx_nodes(self.graph, pos=position, node_size=700, node_color=yellow)

        #Draws the inner circle in the last state
        nodes = nx.draw_networkx_nodes(self.graph, pos=position, node_size=600, node_color=black, nodelist=list(self.finalStates))
        nodes = nx.draw_networkx_nodes(self.graph, pos=position, node_size=500, node_color=yellow, nodelist=list(self.finalStates))

        #Draws the inner circle in the first state
        nodes = nx.draw_networkx_nodes(self.graph, pos=position, node_size=700, node_color=white, nodelist=[self.initialState])

        edge_labels = nx.draw_networkx_edge_labels(self.graph, pos=position, verticalalignment="center")
        arcs = nx.draw_networkx_edges(self.graph, pos=position, connectionstyle='arc3,rad=0.3', node_size=800)
        labels = nx.draw_networkx_labels(self.graph, pos=position)

        plt.show()

class State:                                                # Classe de estado
    def __init__(self, name):
        self.name = name                                    # Nome
        self.transitionsPointingIn = []                     # Transições que estão apontando para este estado
        self.transitionsPointingOut = []                    # Transições que estão apontando a partir deste estado
        self.isFinalState = False
        self.isInitialState = False
    
    def __eq__(self, other):                                # Verifica a igualdade entre dois estados pelo nome
        return self.name == other.name

class Transition:                                                                   # Classe de transição
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
        # create a set to store all visited vertices
        visitedStatesFromInitial = set()
        visitedStatesFromFinalStates = set()
        # Call the recursive helper function
        # to print DFS traversal
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
    

    #Unificação de estados equivalentes
    def unifyEquivalentStates(self):
        self.getEquivalentPairs()
        pass

    def getEquivalentPairs(self):                                           # Verifica quais são os pares equivalentes
        pairsOfStates = self.createPairsToAnalyze()
        combinations = []

        for pairOfStates in pairsOfStates:
            if self.areTwoStatesEquivalent(pairOfStates[0], pairOfStates[1]):
                combinations.append(pairOfStates)

        return combinations

    def createPairsToAnalyze(self):                                         # Cria combinações com todos pares de autômatos
        listOfStates = list(self.statesDictionary.values())
        pairs = list(itertools.combinations(listOfStates, 2))
        
        return pairs

    def areTwoStatesEquivalent(self, firstState, secondState):              # Verifica se dois estados são equivalentes
        if firstState.isInitialState or secondState.isInitialState:
            return False
        
        if firstState.isFinalState != secondState.isFinalState:
            return False

        # Pegar todas as palavras geradas pelo primeiro estado
        # Pegar todas palavras geradas pelo segundo estado
        # Se os dois conjuntos forem diferentes, retornar false
        # Se os dois conjuntos forem iguais, retornar true
        return True
    
    def getAllWordsBetweenTwoStates(self, initialState, finalStates):
        pass
    
main()