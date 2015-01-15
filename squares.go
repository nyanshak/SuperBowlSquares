package main

import (
	"math"
)

const (
	initialSquares		int = 100
)

type Game struct {
	squares				[100]Square
	remainingSquares	int
}

func (self Game) GetRemainingSquares() int {
	return self.remainingSquares
}

func (self Game) AddSquare(square Square) (success bool) {
	num := square.getSquareNum()
	if (self.squares[num].Name == nil) {
		self.squares[num] = square
		self.remainingSquares--
		return true
	} else {
		return false
	}
}

func (self Game) UpdateSquare(square Square) {
	num := square.getSquareNum()
	if (self.squares[num].Name != nil && square.Name != nil) {
		self.squares[num] = square
	} else if (self.squares[num].Name != nil && square.Name == nil) {
		self.squares[num] = square
		self.remainingSquares++
	} else if (self.squares[num].Name == nil && square.Name != nil) {
		self.squares[num] = square
		self.remainingSquares--
	}
}

func (self Game) RemoveSquare(pos int) {
	if (self.squares[pos].Name != nil) {
		self.squares[pos].Name = nil
		self.remainingSquares++
	}
}

type Square struct {
	NfcPos	int
	AfcPos	int
	Name	*string
}

func (self Square) getSquareNum() int {
	return self.AfcPos * 10 + self.NfcPos
}

func getPositions(pos int) (afcPos, nfcPos int) {
	if pos < 0 || pos > initialSquares - 1 {
		return -1, -1
	}
	if pos < 10 {
		return 0, pos
	}
	afcPos = int(math.Mod(float64(pos), 10))
	nfcPos = (pos - afcPos) / 10
	return
}

func NewGame() Game {
	game := new(Game)
	game.remainingSquares = initialSquares
	for i := 0; i < len(game.squares); i++ {
		afcPos, nfcPos := getPositions(i)
		square := Square{NfcPos: nfcPos, AfcPos: afcPos}
		game.squares[i] = square
	}
	return *game
}

func main() {

}
