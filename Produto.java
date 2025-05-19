package org.example;

import javax.persistence.*;

@Entity
public class Produto {
    @Id
    @GeneratedValue
    private Long id;

    private String nome;
    private String categoria;

    // Getters e Setters
    public Long getId() { return id; }
    public String getNome() { return nome; }
    public void setNome(String nome) { this.nome = nome; }
    public String getCategoria() { return categoria; }
    public void setCategoria(String categoria) { this.categoria = categoria; }
}