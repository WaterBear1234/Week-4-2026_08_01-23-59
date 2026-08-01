// A JSON API handler built with only net/http — no framework. Reads a
// request body, validates it, writes a JSON response with a proper status
// code. See ../gin for the same service rebuilt with a framework.
package main

import (
	"encoding/json"
	"log"
	"net/http"
)

type CreateUserRequest struct {
	Name  string `json:"name"`
	Email string `json:"email"`
}

type CreateUserResponse struct {
	ID    int    `json:"id"`
	Name  string `json:"name"`
	Email string `json:"email"`
}

type errorResponse struct {
	Error string `json:"error"`
}

func writeJSON(w http.ResponseWriter, status int, body any) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	json.NewEncoder(w).Encode(body)
}

func createUserHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		writeJSON(w, http.StatusMethodNotAllowed, errorResponse{Error: "POST only"})
		return
	}

	var req CreateUserRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		writeJSON(w, http.StatusBadRequest, errorResponse{Error: "invalid JSON body"})
		return
	}

	// validation — a framework would give middleware for this, net/http
	// makes you write it by hand every time.
	if req.Name == "" {
		writeJSON(w, http.StatusUnprocessableEntity, errorResponse{Error: "name is required"})
		return
	}
	if req.Email == "" {
		writeJSON(w, http.StatusUnprocessableEntity, errorResponse{Error: "email is required"})
		return
	}

	writeJSON(w, http.StatusCreated, CreateUserResponse{ID: 1, Name: req.Name, Email: req.Email})
}

func main() {
	mux := http.NewServeMux()
	mux.HandleFunc("/users", createUserHandler)

	log.Println("bare net/http service listening on :8081")
	log.Fatal(http.ListenAndServe(":8081", mux))
}
