// The exact same service as ../bare, rebuilt with the Echo framework — to
// feel what a framework buys you: routing, a binding/validation helper, and
// middleware, instead of hand-rolling each with net/http.
package main

import (
	"log"
	"net/http"

	"github.com/labstack/echo/v4"
	"github.com/labstack/echo/v4/middleware"
)

type CreateUserRequest struct {
	Name  string `json:"name" validate:"required"`
	Email string `json:"email" validate:"required"`
}

type CreateUserResponse struct {
	ID    int    `json:"id"`
	Name  string `json:"name"`
	Email string `json:"email"`
}

func createUserHandler(c echo.Context) error {
	var req CreateUserRequest
	if err := c.Bind(&req); err != nil { // handles decode errors AND wrong-method routing already
		return c.JSON(http.StatusBadRequest, map[string]string{"error": "invalid JSON body"})
	}

	// echo doesn't validate by default either — same manual checks as the
	// bare version, framework doesn't remove this part.
	if req.Name == "" {
		return c.JSON(http.StatusUnprocessableEntity, map[string]string{"error": "name is required"})
	}
	if req.Email == "" {
		return c.JSON(http.StatusUnprocessableEntity, map[string]string{"error": "email is required"})
	}

	return c.JSON(http.StatusCreated, CreateUserResponse{ID: 1, Name: req.Name, Email: req.Email})
}

func main() {
	e := echo.New()
	e.Use(middleware.Recover()) // one line vs hand-writing panic-recovery middleware

	e.POST("/users", createUserHandler)
	// unlike the bare mux, wrong-method requests to a registered path get a
	// 405 automatically — no manual method check needed.

	log.Println("echo service listening on :8082")
	e.Logger.Fatal(e.Start(":8082"))
}
