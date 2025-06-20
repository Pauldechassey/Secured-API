/// <reference types="cypress" />

describe('Performance Tests', () => {
  beforeEach(() => {
    cy.request({
      method: 'GET',
      url: 'http://localhost:8000/health_strength_checker',
      failOnStatusCode: false
    }).then((response) => {
      expect(response.status).to.equal(200)
    })
  })

  it('should measure password strength check performance', () => {
    const passwords = [
      'Password123!',
      'SuperSecurePassword456!',
      'ComplexP@ssw0rd789'
    ]

    passwords.forEach(password => {
      const start = performance.now()

      cy.request({
        method: 'POST',
        url: 'http://localhost:8000/check_password_strength',
        body: { password },
        failOnStatusCode: false
      }).then((response) => {
        const duration = performance.now() - start
        cy.log(`Temps de réponse pour "${password}": ${duration}ms`)
        expect(duration).to.be.lessThan(1000, 'La vérification devrait prendre moins d\'une seconde')
        expect(response.status).to.equal(200)
      })
    })
  })

  it('should handle concurrent password checks efficiently', () => {
    const numberOfRequests = 10
    const password = 'TestPassword123!'
    const requests = Array(numberOfRequests).fill(null)
    
    const start = performance.now()

    cy.wrap(requests).each(() => {
      return cy.request({
        method: 'POST',
        url: 'http://localhost:8000/check_password_strength',
        body: { password },
        failOnStatusCode: false
      })
    }).then(() => {
      const totalDuration = performance.now() - start
      const averageTime = totalDuration / numberOfRequests
      cy.log(`Temps moyen par requête: ${averageTime}ms`)
      expect(averageTime).to.be.lessThan(500, 'Le temps moyen devrait être inférieur à 500ms')
    })
  })

  it('should maintain performance under load', () => {
    const iterations = 5
    const results: number[] = []

    for(let i = 0; i < iterations; i++) {
      const start = performance.now()
      
      cy.request({
        method: 'POST',
        url: 'http://localhost:8000/check_password_strength',
        body: { password: 'LoadTest123!' },
        failOnStatusCode: false
      }).then((response) => {
        const duration = performance.now() - start
        results.push(duration)
        
        if (i === iterations - 1) {
          const average = results.reduce((a, b) => a + b) / results.length
          const max = Math.max(...results)
          
          cy.log(`Temps moyen: ${average}ms`)
          cy.log(`Temps maximum: ${max}ms`)
          
          expect(average).to.be.lessThan(800, 'Le temps moyen devrait rester stable')
          expect(max).to.be.lessThan(1500, 'Le temps maximum ne devrait pas trop augmenter')
        }
      })
      cy.wait(100)
    }
  })
})