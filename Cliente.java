// src/main/java/org/example/Cliente.java
package org.example;

import javax.persistence.*;

@Entity
public class Cliente {
    @Id
    @GeneratedValue
    private Long id;

    private String nome;
    private String cidade;

    // Getters e Setters
    public Long getId() { return id; }
    public String getNome() { return nome; }
    public void setNome(String nome) { this.nome = nome; }
    public String getCidade() { return cidade; }
    public void setCidade(String cidade) { this.cidade = cidade; }
}